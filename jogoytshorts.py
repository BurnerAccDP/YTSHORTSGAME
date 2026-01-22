import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulador: Desafio dos Espinhos", layout="centered")

st.sidebar.header("Configurações Iniciais")
# Velocidade inicial de rotação (10 é o padrão)
vel_rot_inicial = st.sidebar.slider("Velocidade Inicial dos Espinhos", 1, 50, 10)
# Controle de aceleração das bolas
vel_input = st.sidebar.number_input("Aumento de velocidade das bolas/seg (%)", value=10)
aceleracao = 1 + (vel_input / 100)

modo_jogo = st.sidebar.selectbox("Modo de Jogo", ["Padrão", "Gravidade"])

if st.button("Iniciar Simulação"):
    gravidade_valor = 0.25 if modo_jogo == "Gravidade" else 0
    # Ajuste da escala da velocidade de rotação para o motor gráfico
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
            
            // Tempo e Aumento de Velocidade dos Espinhos (10% a cada 5s)
            let elapsedSecs = Math.floor((Date.now() - startTime) / 1000);
            if (elapsedSecs > 0 && elapsedSecs % 5 === 0 && elapsedSecs !== lastIncrTime) {{
                currentRotationSpeed *= 1.10;
                lastIncrTime = elapsedSecs;
            }}

            // Borda
            ctx.strokeStyle = "white";
            ctx.lineWidth = 5;
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            ctx.stroke();

            // Rotação
            rotationAngle += currentRotationSpeed;

            // Espinhos
            ctx.fillStyle = "#ff4444";
            for (let i = 0; i < 3; i++) {{
                let angle = rotationAngle + (i * 2 * Math.PI / 3);
                ctx.save();
                ctx.translate(centerX, centerY);
                ctx.rotate(angle);
                ctx.beginPath();
                ctx.moveTo(radius, 0);
                ctx.lineTo(radius - 35, -25);
                ctx.lineTo(radius - 35, 25);
                ctx.fill();
                ctx.restore();
            }}

            speedMultiplier *= accelPerFrame;

            for (let i = balls.length - 1; i >= 0; i--) {{
                let b = balls[i];
                b.vy += gravity;
                b.x += b.vx * speedMultiplier;
                b.y += b.vy * speedMultiplier;

                let dx = b.x - centerX;
                let dy = b.y - centerY;
                let dist = Math.sqrt(dx*dx + dy*dy);

                if (dist + b.r >= radius) {{
                    let nx = dx / dist;
                    let ny = dy / dist;
                    
                    b.vx = (b.vx - 2 * (b.vx * nx + b.vy * ny) * nx);
                    b.vy = (b.vy - 2 * (b.vx * nx + b.vy * ny) * ny);
                    
                    b.x = centerX + nx * (radius - b.r - 2);
                    b.y = centerY + ny * (radius - b.r - 2);

                    balls.push(createBall(250, 250));

                    // Verificação de Hit no Espinho
                    let hitAngle = Math.atan2(dy, dx);
                    if (hitAngle < 0) hitAngle += 2 * Math.PI;

                    for (let j = 0; j < 3; j++) {{
                        let spikeAngle = (rotationAngle + (j * 2 * Math.PI / 3)) % (2 * Math.PI);
                        if (spikeAngle < 0) spikeAngle += 2 * Math.PI;
                        let diff = Math.abs(hitAngle - spikeAngle);
                        if (diff < 0.28 || diff > (2*Math.PI - 0.28)) {{
                            balls.splice(i, 1);
                            break;
                        }}
                    }}
                }}

                ctx.fillStyle = b.color;
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.r, 0, Math.PI*2);
                ctx.fill();
            }}
            
            countEl.innerText = balls.length;
            timerEl.innerText = `Tempo: ${{elapsedSecs}}s | Vel. Espinhos: ${{ (currentRotationSpeed * 300).toFixed(1) }}`;

            // Condição de Derrota
            if (balls.length === 0) {{
                gameOver = true;
                statusEl.innerHTML = "<span style='color: #ff4444; font-size: 40px;'>DERROTA!</span><br><small>As bolas acabaram</small>";
                ctx.fillStyle = "rgba(0,0,0,0.7)";
                ctx.fillRect(0,0,500,500);
            }} else {{
                requestAnimationFrame(update);
            }}
        }}
        update();
    </script>
    """
    components.html(html_code, height=650)
else:
    st.info("O desafio começa quando você clicar no botão. Sobreviva!")
