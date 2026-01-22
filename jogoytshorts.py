import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulador: Hitbox Realista", layout="centered")

st.sidebar.header("Configurações Iniciais")
vel_rot_inicial = st.sidebar.slider("Velocidade Inicial dos Espinhos", 1, 50, 10)
vel_input = st.sidebar.number_input("Aumento de velocidade das bolas/seg (%)", value=10)
elasticidade = st.sidebar.slider("Poder do Quique (Bônus de Impulso)", 1.0, 1.5, 1.05, step=0.01)

aceleracao = 1 + (vel_input / 100)
modo_jogo = st.sidebar.selectbox("Modo de Jogo", ["Padrão", "Gravidade"])

if st.button("Iniciar Simulação"):
    gravidade_valor = 0.25 if modo_jogo == "Gravidade" else 0
    rot_base = vel_rot_inicial / 300 
    
    html_code = f"""
    <div style="display: flex; flex-direction: column; align-items: center; background: #111; padding: 20px; border-radius: 20px;">
        <canvas id="canvas" width="500" height="500" style="background:#000; border-radius: 50%; border: 4px solid #444;"></canvas>
        <div style="color: white; font-family: sans-serif; margin-top: 15px; text-align: center;">
            <h2 id="status">Bolas: <span id="count">1</span></h2>
            <p id="timer">Tempo: 0s | Vel. Espinhos: {vel_rot_inicial}</p>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const countEl = document.getElementById('count');
        const timerEl = document.getElementById('timer');
        const statusEl = document.getElementById('status');
        
        const centerX = 250, centerY = 250, radius = 240;
        const bounciness = {elasticidade};
        const spikeHeight = 40; // Altura do espinho para a hitbox
        
        let speedMultiplier = 1.0;
        let rotationAngle = 0;
        let currentRotationSpeed = {rot_base};
        let startTime = Date.now();
        let lastIncrTime = 0;
        let gameOver = false;

        const accelPerFrame = Math.pow({aceleracao}, 1/60);
        const gravity = {gravidade_valor};

        function createBall(x, y) {{
            const angle = Math.random() * Math.PI * 2;
            const speed = 4;
            return {{
                x: x, y: y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                r: 8,
                color: `hsl(${{Math.random() * 360}}, 70%, 60%)`
            }};
        }}

        let balls = [createBall(250, 250)];
        
        function update() {{
            if (gameOver) return;

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            let elapsedSecs = Math.floor((Date.now() - startTime) / 1000);
            if (elapsedSecs > 0 && elapsedSecs % 5 === 0 && elapsedSecs !== lastIncrTime) {{
                currentRotationSpeed *= 1.10;
                lastIncrTime = elapsedSecs;
            }}

            ctx.strokeStyle = "white";
            ctx.lineWidth = 5;
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            ctx.stroke();

            rotationAngle += currentRotationSpeed;

            // Desenho dos Espinhos
            ctx.fillStyle = "#ff4444";
