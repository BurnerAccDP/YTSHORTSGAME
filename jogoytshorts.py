import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulador: Espinhos Giratórios", layout="centered")

st.sidebar.header("Configurações")
# Controle de velocidade de rotação dos espinhos
vel_rotacao = st.sidebar.slider("Velocidade de Rotação dos Espinhos", 0.0, 0.1, 0.03)
# Controle de aceleração das bolas
vel_input = st.sidebar.number_input("Aumento de velocidade das bolas/seg (%)", value=10)
aceleracao = 1 + (vel_input / 100)

modo_jogo = st.sidebar.selectbox("Modo de Jogo", ["Padrão", "Gravidade"])

if st.button("Executar Simulação"):
    gravidade_valor = 0.25 if modo_jogo == "Gravidade" else 0
    
    html_code = f"""
    <div style="display: flex; flex-direction: column; align-items: center;">
        <canvas id="canvas" width="500" height="500" style="background:#111; border-radius: 50%; border: 2px solid #333;"></canvas>
        <h2 style="color: white; font-family: sans-serif;">Bolas: <span id="count">1</span></h2>
    </div>
    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const countEl = document.getElementById('count');
        const centerX = 250, centerY = 250, radius = 240;
        
        let speedMultiplier = 1.0;
        let rotationAngle = 0;
        const accelPerFrame = Math.pow({aceleracao}, 1/60);
        const gravity = {gravidade_valor};

        // Função para criar bola com direção aleatória
        function createBall(x, y) {{
            const angle = Math.random() * Math.PI * 2;
            const speed = 4;
            return {{
                x: x,
                y: y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                r: 8,
                color: `hsl(${{Math.random() * 360}}, 70%, 60%)`
            }};
        }}

        let balls = [createBall(250, 250)];
        
        function update() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Desenha borda do círculo
            ctx.strokeStyle = "white";
            ctx.lineWidth = 5;
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            ctx.stroke();

            // Atualiza rotação dos espinhos
            rotationAngle += {vel_rotacao};

            // Desenha Espinhos Giratórios
            ctx.fillStyle = "#ff4444";
            for (let i = 0; i < 3; i++) {{
                let angle = rotationAngle + (i * 2 * Math.PI / 3);
                ctx.save();
                ctx.translate(centerX, centerY);
                ctx.rotate(angle);
                ctx.beginPath();
                ctx.moveTo(radius, 0);
                ctx.lineTo(radius - 30, -20);
                ctx.lineTo(radius - 30, 20);
                ctx.fill();
                ctx.restore();
            }}

            speedMultiplier *= accelPerFrame;

            for (let i = balls.length - 1; i >= 0; i--) {{
                let b = balls[i];
                
                // Aplica Gravidade e Velocidade
                b.vy += gravity;
                b.x += b.vx * speedMultiplier;
                b.y += b.vy * speedMultiplier;

                let dx = b.x - centerX;
                let dy = b.y - centerY;
                let dist = Math.sqrt(dx*dx + dy*dy);

                // Colisão com a borda circular
                if (dist + b.r >= radius) {{
                    let nx = dx / dist;
                    let ny = dy / dist;
                    
                    // Reflexão (Quique)
                    let dot = b.vx * nx + b.vy * ny;
                    b.vx = (b.vx - 2 * dot * nx);
                    b.vy = (b.vy - 2 * dot * ny);
                    
                    // Empurra um pouco para fora da borda para não travar
                    b.x = centerX + nx * (radius - b.r - 2);
                    b.y = centerY + ny * (radius - b.r - 2);

                    // Spawn nova bola no meio com direção aleatória
                    balls.push(createBall(250, 250));

                    // Verifica colisão com espinhos giratórios
                    let hitAngle = Math.atan2(dy, dx);
                    if (hitAngle < 0) hitAngle += 2 * Math.PI;

                    for (let j = 0; j < 3; j++) {{
                        let spikeAngle = (rotationAngle + (j * 2 * Math.PI / 3)) % (2 * Math.PI);
                        if (spikeAngle < 0) spikeAngle += 2 * Math.PI;
                        
                        let diff = Math.abs(hitAngle - spikeAngle);
                        if (diff < 0.25 || diff > (2*Math.PI - 0.25)) {{
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
            requestAnimationFrame(update);
        }}
        update();
    </script>
    """
    components.html(html_code, height=600)
else:
    st.info("Configure os parâmetros e clique para iniciar.")
