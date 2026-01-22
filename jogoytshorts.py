import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulador: Desafio dos Espinhos", layout="centered")

st.sidebar.header("Configurações")
vel_rot_inicial = st.sidebar.slider("Velocidade Inicial dos Espinhos", 1, 50, 10)
vel_input = st.sidebar.number_input("Aumento de velocidade das bolas/seg (%)", value=10)
elasticidade = st.sidebar.slider("Poder do Quique", 1.0, 1.5, 1.10, step=0.01)

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
        
        const centerX = 250, centerY = 250, radius = 235;
        const bounciness = {elasticidade};
        const spikeHeight = 55; // Espinhos maiores
        
        let speedMultiplier = 1.0;
        let rotationAngle = 0;
        let currentRotationSpeed = {rot_base};
        let startTime = Date.now();
        let lastIncrTime = 0;
        let gameOver = false;

        const accelPerFrame = Math.pow({aceleracao}, 1/60);
        const gravity = {gravidade_valor};

        function createBall(x, y) {{
            // Spawn mais alto (y menor) e impulso inicial aleatório forte
            const angle = (Math.random() * Math.PI) + 0.5; // Direções voltadas para baixo
            const initialPush = 6; 
            return {{
                x: x, y: y,
                vx: Math.cos(angle) * initialPush,
                vy: Math.sin(angle) * initialPush,
                r: 8,
                color: `hsl(${{Math.random() * 360}}, 70%, 60%)`
            }};
        }}

        let balls = [createBall(250, 80)]; // Começa no topo
        
        function update() {{
            if (gameOver) return;

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            let elapsedSecs = Math.floor((Date.now() - startTime) / 1000);
            if (elapsedSecs > 0 && elapsedSecs % 5 === 0 && elapsedSecs !== lastIncrTime) {{
                currentRotationSpeed *= 1.10;
                lastIncrTime = elapsedSecs;
            }}

            ctx.strokeStyle = "white";
            ctx.lineWidth = 6;
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            ctx.stroke();

            rotationAngle += currentRotationSpeed;

            // Desenho dos Espinhos (Hitbox maior visualmente também)
            ctx.fillStyle = "#ff0000";
            for (let i = 0; i < 3; i++) {{
                let angle = rotationAngle + (i * 2 * Math.PI / 3);
                ctx.save();
                ctx.translate(centerX, centerY);
                ctx.rotate(angle);
                ctx.beginPath();
                ctx.moveTo(radius, 0);
                ctx.lineTo(radius - spikeHeight, -35); // Mais largo
                ctx.lineTo(radius - spikeHeight, 35);  // Mais largo
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

                // Hitbox Angular do Espinho (Aumentada para 0.35 rad)
                let ballAngle = Math.atan2(dy, dx);
                if (ballAngle < 0) ballAngle += 2 * Math.PI;

                let hitSpike = false;
                for (let j = 0; j < 3; j++) {{
                    let spikeAngle = (rotationAngle + (j * 2 * Math.PI / 3)) % (2 * Math.PI);
                    if (spikeAngle < 0) spikeAngle += 2 * Math.PI;
                    
                    let diff = Math.abs(ballAngle - spikeAngle);
                    if (diff > Math.PI) diff = 2 * Math.PI - diff;

                    if (diff < 0.35 && dist > (radius - spikeHeight - b.r)) {{
                        balls.splice(i, 1);
                        hitSpike = true;
                        break;
                    }
                }

                if (!hitSpike) {{
                    // Colisão com a borda - FÍSICA MELHORADA PARA NÃO GRUDAR
                    if (dist + b.r >= radius) {{
                        let nx = dx / dist;
                        let ny = dy / dist;
                        let dot = b.vx * nx + b.vy * ny;
                        
                        // Reflete e aplica bounciness
                        b.vx = (b.vx - 2 * dot * nx) * bounciness;
                        b.vy = (b.vy - 2 * dot * ny) * bounciness;
                        
                        // TELEPORTE DE SEGURANÇA (Anti-grude)
                        b.x = centerX + nx * (radius - b.r - 5);
                        b.y = centerY + ny * (radius - b.r - 5);

                        // Spawn de uma nova no topo
                        balls.push(createBall(250, 80));
                    }}

                    ctx.fillStyle = b.color;
                    ctx.beginPath();
                    ctx.arc(b.x, b.y, b.r, 0, Math.PI*2);
                    ctx.fill();
                }}
            }
            
            countEl.innerText = balls.length;
            timerEl.innerText = `Tempo: ${{elapsedSecs}}s | Vel. Espinhos: ${{ (currentRotationSpeed * 300).toFixed(1) }}`;

            if (balls.length === 0) {{
                gameOver = true;
                statusEl.innerHTML = "<span style='color: #ff0000; font-size: 45px; font-weight: bold;'>GAME OVER</span>";
                ctx.fillStyle = "rgba(0,0,0,0.85)";
                ctx.fillRect(0,0,500,500);
            }} else {{
                requestAnimationFrame(update);
            }}
        }}
        update();
    </script>
    """
    components.html(html_code, height=650)
