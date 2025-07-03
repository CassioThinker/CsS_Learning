class SpriteAnimation:
    def __init__(self, frames, frame_duration=0.2):
        # Lista de imagens (frames) que compõem a animação
        self.frames = frames
        # Duração de cada frame em segundos
        self.frame_duration = frame_duration
        # Índice do frame atual da animação
        self.current_frame = 0
        # Tempo acumulado desde a última troca de frame
        self.time_since_last_frame = 0

    def update(self, dt):
        # Atualiza o tempo acumulado com o tempo decorrido desde o último frame
        self.time_since_last_frame += dt
        # Se passou o tempo suficiente, avança para o próximo frame
        if self.time_since_last_frame >= self.frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.time_since_last_frame = 0

    def get_current_frame(self):
        # Retorna o frame (imagem) atual da animação
        return self.frames[self.current_frame]
