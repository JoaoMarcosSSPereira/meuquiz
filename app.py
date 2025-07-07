from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import json
import os
import random
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from io import BytesIO

app = Flask(__name__)
app.secret_key = "desafio-do-conhecimento-secret-key"

# ========== CONFIGURAÇÃO DOS GURUS ==========
MASTERS = {
    'conhecimento_basico': {
        'title': "Guru do Conhecimento Básico",
        'desc': "Teste seus fundamentos em dados e tecnologia.",
        'questions': [
            {"question": "Qual é a principal linguagem de programação para análise de dados e machine learning?", "options": ["Java", "Python", "C++", "Ruby"], "correct": 1},
            {"question": "Qual termo descreve o processo de extrair insights de grandes conjuntos de dados?", "options": ["Desenvolvimento Web", "Mineração de Dados", "Design Gráfico", "Engenharia de Software"], "correct": 1},
            {"question": "Qual das seguintes opções é um tipo de banco de dados NoSQL?", "options": ["MySQL", "PostgreSQL", "MongoDB", "SQLite"], "correct": 2},
            {"question": "O que significa a sigla 'API' em desenvolvimento de software?", "options": ["Advanced Programming Interface", "Application Programming Interface", "Automated Process Integration", "Algorithmic Protocol Instruction"], "correct": 1},
            {"question": "Qual tecnologia é usada para criar páginas web interativas no lado do cliente?", "options": ["Python", "PHP", "JavaScript", "SQL"], "correct": 2},
            {"question": "Qual é o nome da nuvem de computação da Amazon?", "options": ["Azure", "Google Cloud Platform", "AWS", "Heroku"], "correct": 2},
            {"question": "O que é um 'framework' em desenvolvimento de software?", "options": ["Uma ferramenta para depuração de código", "Um conjunto de bibliotecas e ferramentas para construir aplicações", "Um tipo de linguagem de programação", "Um sistema operacional"], "correct": 1},
            {"question": "Qual protocolo é usado para comunicação segura na internet?", "options": ["HTTP", "FTP", "SMTP", "HTTPS"], "correct": 3},
            {"question": "O que é 'Big Data'?", "options": ["Um banco de dados muito grande", "Um conjunto de dados tão grande e complexo que métodos tradicionais não conseguem processar", "Um tipo de algoritmo de compressão de dados", "Uma nova linguagem de programação"], "correct": 1},
            {"question": "Qual das seguintes opções é um sistema de controle de versão distribuído?", "options": ["SVN", "Git", "CVS", "Mercurial"], "correct": 1}
        ]
    },
    'desafios_tecnicos': {
        'title': "Guru dos Desafios Técnicos",
        'desc': "Aprofunde-se em conceitos técnicos avançados.",
        'questions': [
            {"question": "Qual o principal objetivo da metodologia DevOps?", "options": ["Aumentar a burocracia no desenvolvimento", "Integrar desenvolvimento e operações para agilizar a entrega de software", "Reduzir a comunicação entre equipes", "Apenas automatizar testes"], "correct": 1},
            {"question": "O que é um 'container' em computação?", "options": ["Um tipo de servidor físico", "Uma unidade padronizada de software que empacota código e todas as suas dependências", "Um sistema de arquivos para armazenamento de dados", "Uma ferramenta de monitoramento de rede"], "correct": 1},
            {"question": "Qual o nome da linguagem de consulta padrão para bancos de dados relacionais?", "options": ["Python", "Java", "SQL", "NoSQL"], "correct": 2},
            {"question": "O que é 'Machine Learning'?", "options": ["Um novo tipo de hardware", "A capacidade de sistemas aprenderem e melhorarem a partir de dados sem serem explicitamente programados", "Um software para edição de vídeo", "Uma técnica de criptografia"], "correct": 1},
            {"question": "Qual o conceito de 'Cloud Computing'?", "options": ["Armazenar dados em um HD externo", "Usar servidores locais para processamento", "Entrega de recursos de computação sob demanda pela internet, com pagamento pelo uso", "Desenvolvimento de aplicativos offline"], "correct": 2},
            {"question": "Qual das seguintes opções é uma plataforma de orquestração de containers?", "options": ["Docker Compose", "Kubernetes", "Vagrant", "Ansible"], "correct": 1},
            {"question": "O que é 'Inteligência Artificial' (IA)?", "options": ["Um robô que pensa sozinho", "A simulação de processos de inteligência humana por máquinas", "Um tipo de vírus de computador", "Um sistema de segurança de rede"], "correct": 1},
            {"question": "Qual o objetivo de um 'Data Warehouse'?", "options": ["Armazenar dados temporários", "Servir como um banco de dados operacional para transações diárias", "Consolidar dados de diversas fontes para análise e relatórios", "Executar aplicações web"], "correct": 2},
            {"question": "O que é 'Version Control System' (VCS)?", "options": ["Um software para controle de estoque", "Um sistema que registra mudanças em um conjunto de arquivos ao longo do tempo", "Uma ferramenta para gerenciar projetos de design", "Um tipo de firewall"], "correct": 1},
            {"question": "Qual das seguintes opções é um exemplo de linguagem de programação orientada a objetos?", "options": ["C", "Assembly", "Fortran", "Java"], "correct": 3}
        ]
    },
    'comportamental': {
        'title': "Guru Comportamental",
        'desc': "Avalie suas habilidades interpessoais e de resolução de problemas.",
        'questions': [
            {"question": "Descreva uma situação em que você falhou e o que aprendeu com ela.", "options": ["Não lembro de nenhuma falha", "Explico a falha e o plano de ação para evitar que aconteça novamente", "Culpo a equipe ou as circunstâncias externas"], "correct": 1},
            {"question": "Como você lida com prazos apertados e pressão?", "options": ["Fico estressado e desisto", "Organizo minhas tarefas, priorizo e peço ajuda se necessário", "Trabalho até a exaustão, sem me preocupar com a qualidade"], "correct": 1},
            {"question": "Como você se mantém atualizado sobre novas tecnologias?", "options": ["Espero que a empresa me treine", "Leio artigos, faço cursos online e participo de comunidades", "Apenas uso o que já sei"], "correct": 1},
            {"question": "Descreva uma situação em que você teve que trabalhar com alguém de difícil convivência. Como você lidou com isso?", "options": ["Evitei a pessoa ao máximo", "Tentei entender o ponto de vista dela e encontrar um terreno comum para colaborar", "Confrontei a pessoa publicamente"], "correct": 1},
            {"question": "Qual é a sua maior fraqueza e como você está trabalhando para melhorá-la?", "options": ["Não tenho fraquezas", "Menciono uma fraqueza real e o que estou fazendo para superá-la", "Menciono uma fraqueza que na verdade é uma qualidade disfarçada"], "correct": 1}
        ]
    }
}

@app.route('/')
def index():
    return render_template('index.html', masters=MASTERS)

@app.route('/start', methods=['POST'])
def start_game():
    player_name = request.form.get('player_name', '').strip()
    selected_guru_key = request.form.get('guru_selection')
    if not player_name:
        flash("Por favor, digite seu nome para iniciar o desafio!")
        return redirect(url_for('index'))
    if selected_guru_key not in MASTERS:
        flash("Guru selecionado inválido. Por favor, escolha um guru válido.")
        return redirect(url_for('index'))
    session.clear()
    session['player_name'] = player_name
    session['selected_guru_key'] = selected_guru_key
    session['score'] = 0
    session['question_index'] = 0
    session['player_answers'] = []
    guru_questions = list(MASTERS[selected_guru_key]['questions']) # cópia para embaralhar
    random.shuffle(guru_questions)
    session['questions'] = guru_questions
    return redirect(url_for('question_page'))

@app.route('/question', methods=['GET'])
def question_page():
    if 'player_name' not in session or 'questions' not in session or 'selected_guru_key' not in session:
        return redirect(url_for('index'))
    questions_list = session.get('questions', [])
    current_index = session.get('question_index', 0)
    selected_guru_key = str(session.get('selected_guru_key'))
    guru_title = MASTERS.get(selected_guru_key, {}).get('title', 'Guru Desconhecido')
    if current_index >= len(questions_list):
        return redirect(url_for('result_page'))
    current_question = questions_list[current_index]
    return render_template('question.html',
                           question=current_question,
                           current_q_num=current_index + 1,
                           total_q_num=len(questions_list),
                           score=session.get('score', 0),
                           guru_title=guru_title)

@app.route('/answer', methods=['POST'])
def answer_question():
    if 'player_name' not in session or 'questions' not in session or 'selected_guru_key' not in session:
        return redirect(url_for('index'))
    questions_list = session.get('questions', [])
    current_index = session.get('question_index', 0)
    if current_index >= len(questions_list):
        return redirect(url_for('result_page'))
    current_question = questions_list[current_index]
    selected_option_text = request.form.get('selected_option')
    correct_option_index = current_question['correct']
    correct_option_text = current_question['options'][correct_option_index]
    is_correct = selected_option_text == correct_option_text
    if is_correct:
        session['score'] += 1
        flash("✅ Resposta correta!")
    else:
        flash(f"❌ Resposta incorreta. A resposta correta era: '{correct_option_text}'.")
    player_answers = session.get('player_answers', [])
    player_answers.append({
        'question': current_question['question'],
        'chosen_option': selected_option_text,
        'correct_option': correct_option_text,
        'is_correct': is_correct
    })
    session['player_answers'] = player_answers
    session['question_index'] += 1

    # ===== Salva histórico XLS =====
    historico_path = os.path.join(app.root_path, 'dados_historico.xlsx')
    novo_df = pd.DataFrame([{
        "Jogador": session['player_name'],
        "Guru": MASTERS[session['selected_guru_key']]['title'],
        "Data": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "Pergunta": current_question['question'],
        "Escolhida": selected_option_text,
        "Correta": correct_option_text,
        "Acertou": "Sim" if is_correct else "Não"
    }])
    if os.path.exists(historico_path):
        antigo_df = pd.read_excel(historico_path)
        combinado_df = pd.concat([antigo_df, novo_df], ignore_index=True)
    else:
        combinado_df = novo_df
    combinado_df.to_excel(historico_path, index=False)

    return redirect(url_for('question_page'))

@app.route('/result', methods=['GET'])
def result_page():
    if 'player_name' not in session or 'selected_guru_key' not in session:
        return redirect(url_for('index'))
    player_name = session.get('player_name', 'Jogador')
    final_score = session.get('score', 0)
    total_questions = len(session.get('questions', []))
    selected_guru_key = str(session.get('selected_guru_key'))
    guru_title = MASTERS.get(selected_guru_key, {}).get('title', 'Guru Desconhecido')
    return render_template('result.html',
                           player_name=player_name,
                           final_score=final_score,
                           total_questions=total_questions,
                           guru_title=guru_title)

@app.route('/download_results_xls', methods=['GET'])
def download_results_xls():
    if 'player_name' not in session or 'player_answers' not in session:
        flash("Nenhum resultado de jogo para baixar.")
        return redirect(url_for('index'))
    player_name = session.get('player_name', 'Jogador_Anonimo')
    guru_key = str(session.get('selected_guru_key', 'desconhecido'))
    guru_title = MASTERS.get(guru_key, {}).get('title', 'Desconhecido')
    answers = session.get('player_answers', [])
    score = session.get('score', 0)
    total = len(session.get('questions', []))
    wb = Workbook()
    ws = wb.active
    ws.title = "Resultado do Jogo"
    ws.append(['Nome do Jogador', 'Guru', 'Pontuação', 'Total de Perguntas'])
    ws.append([player_name, guru_title, score, total])
    ws.append([])
    ws.append(['Pergunta', 'Escolhida', 'Correta', 'Acertou?'])
    for ans in answers:
        ws.append([
            ans['question'],
            ans['chosen_option'],
            ans['correct_option'],
            'Sim' if ans['is_correct'] else 'Não'
        ])
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f"respostas_{player_name.replace(' ', '_')}_{guru_key}.xlsx"
    return send_file(output,
                     as_attachment=True,
                     download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/ranking', methods=['GET'])
def show_ranking():
    historico_path = os.path.join(app.root_path, 'dados_historico.xlsx')
    if not os.path.exists(historico_path):
        flash("Nenhum histórico encontrado para gerar ranking.")
        return redirect(url_for('index'))
    df = pd.read_excel(historico_path)
    ranking_df = df.groupby(["Jogador", "Guru"]).agg(
        Total_Respostas=pd.NamedAgg(column="Pergunta", aggfunc="count"),
        Acertos=pd.NamedAgg(column="Acertou", aggfunc=lambda x: (x == "Sim").sum())
    ).reset_index()
    ranking_df["% Acertos"] = (ranking_df["Acertos"] / ranking_df["Total_Respostas"] * 100).round(1)
    ranking = ranking_df.to_dict(orient='records')
    return render_template('ranking.html', ranking=ranking)

@app.after_request
def add_security_headers(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # CSP liberada para teste/portfólio, permite inline e qualquer fonte/style
    response.headers['Content-Security-Policy'] = "default-src *; script-src * 'unsafe-inline' 'unsafe-eval'; style-src * 'unsafe-inline'; font-src *"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

if __name__ == '__main__':
    app.run(debug=True)
    
