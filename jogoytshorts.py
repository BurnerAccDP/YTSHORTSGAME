import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulador de Bolinhas", layout="centered")

st.sidebar.header("Configurações")
vel_input = st.sidebar.number_input("Aumento de velocidade por segundo (%)", value=10)
aceleracao = 1 + (vel_input / 100)

modo_jogo = st.sidebar.selectbox("Modo de Jogo", ["Padrão", "Gravidade Zero", "Chaos Mode (Em breve)"])

if st.button("Executar Simulação"):
    # Código HTML/JS para rodar a animação
    html_code = f"""
    <canvas id="canvas" width="500" height="500" style="background:#111; border-radius: 50%; display: block; margin: auto;"></canvas>
    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const centerX = 250, centerY = 250, radius = 240;
        let speedMultiplier = 1.0;
        const accelPerFrame = Math.pow({aceleracao}, 1/60); // Ajuste para 60fps

        let balls = [{{ x: 250, y: 250, vx: 2, vy: 3, r: 8, color: '#00ffcc' }}];
        
        // Espinhos (3 triângulos fixos na borda)
        const spikes = [
            {{ angle: 0 }},
            {{ angle: (2 * Math.PI) / 3 }},
            {{ angle: (4 * Math.PI) / 3 }}
        ];

        function drawSpikes() {{
            ctx.fillStyle = "red";
            spikes.forEach(s => {{
                ctx.save();
                ctx.translate(centerX, centerY);
                ctx.rotate(s.angle);
                ctx.beginPath();
                ctx.moveTo(radius, 0);
                ctx.lineTo(radius - 25, -15);
                ctx.lineTo(radius - 25, 15);
                ctx.fill();
                ctx.restore();
            }});
        }}

        function update() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Desenha o círculo limite
            ctx.strokeStyle = "white";
            ctx.lineWidth = 5;
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            ctx.stroke();

            drawSpikes();

            speedMultiplier *= accelPerFrame;

            for (let i = balls.length - 1; i >= 0; i--) {{
                let b = balls[i];
                b.x += b.vx * speedMultiplier;
                b.y += b.vy * speedMultiplier;

                let dx = b.x - centerX;
                let dy = b.y - centerY;
                let dist = Math.sqrt(dx*dx + dy*dy);

                // Colisão com a borda
                if (dist + b.r >= radius) {{
                    // Reflexão vetorial
                    let nx = dx / dist;
                    let ny = dy / dist;
                    let dot = b.vx * nx + b.vy * ny;
                    b.vx -= 2 * dot * nx;
                    b.vy -= 2 * dot * ny;
                    
                    // Reposiciona para não prender
                    b.x = centerX + nx * (radius - b.r - 1);
                    b.y = centerY + ny * (radius - b.r - 1);

                    // Spawn nova bola no meio
                    balls.push({{ x: 250, y: 250, vx: Math.random()*4-2, vy: Math.random()*4-2, r: 8, color: 'hsl('+Math.random()*360+', 70%, 60%)' }});

                    // Verifica se bateu no espinho
                    let hitAngle = Math.atan2(dy, dx);
                    if (hitAngle < 0) hitAngle += 2 * Math.PI;

                    spikes.forEach(s => {{
                        let diff = Math.abs(hitAngle - s.angle);
                        if (diff < 0.2 || diff > (2*Math.PI - 0.2)) {{
                            balls.splice(i, 1);
                        }}
                    }});
                }}

                ctx.fillStyle = b.color;
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.r, 0, Math.PI*2);
                ctx.fill();
            }}
            requestAnimationFrame(update);
        }}
        update();
    </script>
    """
    components.html(html_code, height=550)
else:
    st.info("Clique no botão para iniciar a simulação.")