#!/usr/bin/env python3
"""
Script para combinar vídeos em um único arquivo.
"""
import os
import sys
import logging
import argparse
import subprocess
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('combinar_videos')

def criar_diretorios():
    """
    Cria os diretórios necessários para o funcionamento do script.
    """
    diretorios = [
        "output/videos/final"
    ]

    for diretorio in diretorios:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
            logger.info(f"Diretório criado: {diretorio}")

def combinar_videos(video_files, output_file=None, transition="fade", transition_duration=0.5,
                audio_files=None, audio_delay=0.0, use_original_audio=False):
    """
    Combina vários vídeos em um único arquivo.

    Args:
        video_files: Lista de caminhos para os arquivos de vídeo
        output_file: Caminho para o arquivo de saída (opcional)
        transition: Tipo de transição entre os vídeos (opcional)
        transition_duration: Duração da transição em segundos (opcional)
        audio_files: Lista de caminhos para os arquivos de áudio (opcional)
        audio_delay: Atraso do áudio em segundos (pode ser negativo para adiantar) (opcional)
        use_original_audio: Se True, usa os arquivos de áudio originais em vez do áudio dos vídeos (opcional)

    Returns:
        str: Caminho para o vídeo combinado, ou None em caso de erro
    """
    if not video_files:
        logger.error("Nenhum arquivo de vídeo fornecido.")
        return None

    # Verificar se os arquivos existem
    for video_file in video_files:
        if not os.path.exists(video_file):
            logger.error(f"Arquivo não encontrado: {video_file}")
            return None

    # Definir nome do arquivo de saída
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join("output", "videos", "final", f"rapidinha_final_{timestamp}.mp4")

    # Criar diretório de saída se não existir
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    try:
        # Criar arquivo de lista de vídeos temporário
        list_file = os.path.join("output", "videos", "temp_list.txt")
        with open(list_file, "w") as f:
            for video_file in video_files:
                f.write(f"file '{os.path.abspath(video_file)}'\n")

        # Comando FFmpeg para combinar vídeos
        if transition == "none":
            # Sem transição, apenas concatenar
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", list_file,
                "-c", "copy",
                output_file
            ]
        else:
            # Com transição, precisa recodificar
            # Primeiro, vamos obter informações sobre o primeiro vídeo
            probe_cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate",
                "-of", "json",
                video_files[0]
            ]

            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            if probe_result.returncode != 0:
                logger.error(f"Erro ao obter informações do vídeo: {probe_result.stderr}")
                return None

            import json
            video_info = json.loads(probe_result.stdout)
            width = video_info["streams"][0]["width"]
            height = video_info["streams"][0]["height"]
            frame_rate = eval(video_info["streams"][0]["r_frame_rate"])

            # Criar filtro de transição
            filter_complex = []
            for i in range(len(video_files)):
                filter_complex.append(f"[{i}:v]scale={width}:{height},setsar=1[v{i}]")

            for i in range(len(video_files) - 1):
                if transition == "fade":
                    # Transição com fade
                    filter_complex.append(f"[v{i}][v{i+1}]xfade=transition=fade:duration={transition_duration}:offset={i*5}[v{i+1}_t]")
                elif transition == "dissolve":
                    # Transição com dissolve
                    filter_complex.append(f"[v{i}][v{i+1}]xfade=transition=dissolve:duration={transition_duration}:offset={i*5}[v{i+1}_t]")
                elif transition == "wipe":
                    # Transição com wipe
                    filter_complex.append(f"[v{i}][v{i+1}]xfade=transition=wiperight:duration={transition_duration}:offset={i*5}[v{i+1}_t]")

            # Comando FFmpeg com filtro complexo
            cmd = [
                "ffmpeg",
                "-y"
            ]

            # Adicionar inputs
            for video_file in video_files:
                cmd.extend(["-i", video_file])

            # Verificar se devemos usar áudio original
            if use_original_audio and audio_files and len(audio_files) == len(video_files):
                logger.info("Usando arquivos de áudio originais")

                # Adicionar inputs de áudio
                for audio_file in audio_files:
                    cmd.extend(["-i", audio_file])

                # Criar filtros para áudio com ajuste de sincronização
                audio_filters = []
                audio_offset = len(video_files)  # Índice dos inputs de áudio

                for i in range(len(audio_files)):
                    # Aplicar atraso de áudio se necessário
                    if audio_delay > 0:
                        # Atraso positivo: atrasar o áudio
                        audio_filters.append(f"[{audio_offset + i}:a]adelay={int(audio_delay * 1000)}|{int(audio_delay * 1000)}[a{i}]")
                    elif audio_delay < 0:
                        # Atraso negativo: adiantar o áudio (atrasar o vídeo)
                        # Não podemos adiantar o áudio, então vamos atrasar o vídeo
                        # Modificar os filtros de vídeo para incluir o atraso
                        filter_complex[i] = f"[{i}:v]setpts=PTS+{abs(audio_delay)}/TB,scale={width}:{height},setsar=1[v{i}]"
                        audio_filters.append(f"[{audio_offset + i}:a]acopy[a{i}]")
                    else:
                        audio_filters.append(f"[{audio_offset + i}:a]acopy[a{i}]")

                # Adicionar filtro complexo para vídeo e áudio
                filter_complex_str = ";".join(filter_complex) + ";" + ";".join(audio_filters)

                # Adicionar concatenação de áudio se houver mais de um áudio
                if len(audio_files) > 1:
                    audio_concat_inputs = "".join([f"[a{i}]" for i in range(len(audio_files))])
                    filter_complex_str += f";{audio_concat_inputs}concat=n={len(audio_files)}:v=0:a=1[aout]"

                    cmd.extend([
                        "-filter_complex",
                        filter_complex_str,
                        "-map", f"[v{len(video_files)-1}_t]",
                        "-map", "[aout]",
                        "-c:v", "libx264",
                        "-c:a", "aac",
                        "-preset", "medium",
                        "-crf", "23",
                        output_file
                    ])
                else:
                    # Se houver apenas um áudio
                    cmd.extend([
                        "-filter_complex",
                        filter_complex_str,
                        "-map", f"[v{len(video_files)-1}_t]",
                        "-map", f"[a0]",
                        "-c:v", "libx264",
                        "-c:a", "aac",
                        "-preset", "medium",
                        "-crf", "23",
                        output_file
                    ])
            else:
                # Usar áudio dos vídeos
                # Criar filtros para áudio
                audio_filters = []
                for i in range(len(video_files)):
                    # Aplicar atraso de áudio se necessário
                    if audio_delay > 0:
                        # Atraso positivo: atrasar o áudio
                        audio_filters.append(f"[{i}:a]adelay={int(audio_delay * 1000)}|{int(audio_delay * 1000)}[a{i}]")
                    elif audio_delay < 0:
                        # Atraso negativo: adiantar o áudio (atrasar o vídeo)
                        # Não podemos adiantar o áudio, então vamos atrasar o vídeo
                        # Modificar os filtros de vídeo para incluir o atraso
                        filter_complex[i] = f"[{i}:v]setpts=PTS+{abs(audio_delay)}/TB,scale={width}:{height},setsar=1[v{i}]"
                        audio_filters.append(f"[{i}:a]")
                    else:
                        audio_filters.append(f"[{i}:a]")

                # Adicionar filtro complexo para vídeo e áudio
                filter_complex_str = ";".join(filter_complex)

                # Adicionar filtros de áudio se houver atraso
                if audio_delay != 0:
                    filter_complex_str += ";" + ";".join(audio_filters)
                    audio_concat_inputs = "".join([f"[a{i}]" for i in range(len(video_files))])
                else:
                    audio_concat_inputs = "".join(audio_filters)

                # Adicionar concatenação de áudio se houver mais de um vídeo
                if len(video_files) > 1:
                    filter_complex_str += f";{audio_concat_inputs}concat=n={len(video_files)}:v=0:a=1[aout]"
                    cmd.extend([
                        "-filter_complex",
                        filter_complex_str,
                        "-map", f"[v{len(video_files)-1}_t]",
                        "-map", "[aout]",
                        "-c:v", "libx264",
                        "-c:a", "aac",
                        "-preset", "medium",
                        "-crf", "23",
                        output_file
                    ])
                else:
                    # Se houver apenas um vídeo
                    if audio_delay != 0:
                        cmd.extend([
                            "-filter_complex",
                            filter_complex_str,
                            "-map", f"[v{len(video_files)-1}_t]",
                            "-map", "[a0]",
                            "-c:v", "libx264",
                            "-c:a", "aac",
                            "-preset", "medium",
                            "-crf", "23",
                            output_file
                        ])
                    else:
                        cmd.extend([
                            "-filter_complex",
                            filter_complex_str,
                            "-map", f"[v{len(video_files)-1}_t]",
                            "-map", "0:a",
                            "-c:v", "libx264",
                            "-c:a", "aac",
                            "-preset", "medium",
                            "-crf", "23",
                            output_file
                        ])

        # Executar comando
        logger.info(f"Executando comando: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

        # Remover arquivo de lista temporário
        if os.path.exists(list_file):
            os.remove(list_file)

        logger.info(f"Vídeos combinados com sucesso: {output_file}")
        return output_file

    except Exception as e:
        logger.error(f"Erro ao combinar vídeos: {e}")
        return None

def abrir_arquivo(file_path):
    """
    Abre um arquivo com o aplicativo padrão do sistema.

    Args:
        file_path: Caminho para o arquivo
    """
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return

    try:
        import platform
        import subprocess

        system = platform.system()

        if system == "Darwin":  # macOS
            subprocess.call(["open", file_path])
        elif system == "Windows":
            subprocess.call(["start", file_path], shell=True)
        else:  # Linux e outros
            subprocess.call(["xdg-open", file_path])

        logger.info(f"Arquivo aberto: {file_path}")

    except Exception as e:
        logger.error(f"Erro ao abrir arquivo: {e}")

def main():
    """
    Função principal.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Combinador de vídeos para o FlukakuIA")
    parser.add_argument("--videos", nargs="+", help="Lista de caminhos para os arquivos de vídeo")
    parser.add_argument("--audios", nargs="+", help="Lista de caminhos para os arquivos de áudio originais")
    parser.add_argument("--output", help="Caminho para o arquivo de saída")
    parser.add_argument("--transition", choices=["none", "fade", "dissolve", "wipe"], default="fade", help="Tipo de transição entre os vídeos")
    parser.add_argument("--transition-duration", type=float, default=0.5, help="Duração da transição em segundos")
    parser.add_argument("--audio-delay", type=float, default=0.0, help="Atraso do áudio em segundos (pode ser negativo para adiantar)")
    parser.add_argument("--use-original-audio", action="store_true", help="Usar os arquivos de áudio originais em vez do áudio dos vídeos")
    parser.add_argument("--no-abrir", action="store_true", help="Não abrir o arquivo gerado")
    parser.add_argument("--debug", action="store_true", help="Ativar modo de depuração")

    args = parser.parse_args()

    # Configurar nível de log
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Criar diretórios necessários
    criar_diretorios()

    # Se não foram fornecidos vídeos, procurar os mais recentes
    if not args.videos:
        import glob

        # Encontrar os vídeos mais recentes
        video_files = sorted(glob.glob("output/videos/rapidinha_video_secao_*.mp4"), key=os.path.getmtime, reverse=True)

        if not video_files:
            logger.error("Nenhum arquivo de vídeo encontrado.")
            return 1

        # Usar os dois primeiros vídeos
        video_files = video_files[:2]

        # Ordenar por número de seção
        video_files = sorted(video_files, key=lambda x: int(os.path.basename(x).split("_")[3]))

        logger.info(f"Usando os vídeos mais recentes:")
        for video_file in video_files:
            logger.info(f"  - {video_file}")
    else:
        video_files = args.videos

    # Se não foram fornecidos áudios e use_original_audio é True, procurar os áudios correspondentes
    audio_files = args.audios
    if args.use_original_audio and not audio_files:
        import glob

        # Tentar encontrar os áudios correspondentes
        audio_files = []
        for video_file in video_files:
            # Extrair o número da seção do nome do arquivo de vídeo
            try:
                secao = os.path.basename(video_file).split("_")[3]
                # Encontrar o áudio correspondente
                audio_pattern = f"output/audio/rapidinha_secao_{secao}_*.mp3"
                matching_audios = sorted(glob.glob(audio_pattern), key=os.path.getmtime, reverse=True)

                if matching_audios:
                    audio_files.append(matching_audios[0])
                    logger.info(f"Áudio encontrado para seção {secao}: {matching_audios[0]}")
                else:
                    logger.warning(f"Nenhum áudio encontrado para seção {secao}")
                    args.use_original_audio = False
                    break
            except (IndexError, ValueError):
                logger.warning(f"Não foi possível extrair o número da seção do arquivo: {video_file}")
                args.use_original_audio = False
                break

        if args.use_original_audio and len(audio_files) != len(video_files):
            logger.warning("Número de arquivos de áudio não corresponde ao número de vídeos")
            args.use_original_audio = False
            audio_files = None

    # Combinar vídeos
    output_file = combinar_videos(
        video_files,
        args.output,
        args.transition,
        args.transition_duration,
        audio_files,
        args.audio_delay,
        args.use_original_audio
    )

    if output_file:
        logger.info(f"Vídeo combinado com sucesso: {output_file}")

        # Abrir o arquivo se solicitado
        if not args.no_abrir:
            abrir_arquivo(output_file)
    else:
        logger.error("Falha ao combinar vídeos.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
