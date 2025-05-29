import os
from typing import List
import click
from PIL import Image, ImageDraw, ImageFont, ImageFont as PILImageFont


def add_font_name_line(font_path: str, text: str) -> str:
    """
    폰트 파일에서 실제 폰트 이름을 추출하여 텍스트 상단에 추가합니다.

    Args:
        font_path: 사용할 .ttf 폰트 파일의 경로.
        text: 이미지로 변환할 텍스트.

    Returns:
        폰트 이름이 포함된 텍스트 문자열.
    """
    try:
        font = ImageFont.truetype(font_path, 10)
        font_name = font.getname()[0]
        return f"Font: {font_name}\n\n{text}"
    except Exception:
        return text


def create_text_image(
    text: str, font_path: str, font_size: int, output_filename: str
) -> None:
    """
    단일 텍스트를 이미지로 생성합니다.

    Args:
        text: 이미지로 변환할 텍스트.
        font_path: 사용할 .ttf 폰트 파일의 경로.
        font_size: 폰트 크기.
        output_filename: 생성될 이미지 파일의 이름.
    """
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Error: Font file not found or could not be opened at {font_path}")
        return

    # 텍스트 크기 계산
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = bottom - top

    padding = 20
    image_width = text_width + 2 * padding
    image_height = text_height + 2 * padding

    image = Image.new("RGB", (image_width, image_height), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((padding, padding), text, font=font, fill="black")
    image.save(output_filename)


def wrap_text(text: str, font: PILImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """
    텍스트를 최대 너비에 맞춰 여러 줄로 나눕니다.

    Args:
        text: 줄바꿈할 원본 텍스트.
        font: PIL ImageFont 객체.
        max_width: 한 줄의 최대 너비(픽셀).

    Returns:
        줄바꿈된 텍스트 리스트.
    """
    if not text:
        return []

    lines: List[str] = []
    words = text.split(" ")
    current_line: List[str] = []
    current_line_width = 0
    space_width = font.getlength(" ")

    for word in words:
        word_width = font.getlength(word)
        add_space = space_width if current_line else 0
        if current_line_width + add_space + word_width <= max_width:
            if current_line:
                current_line_width += space_width
            current_line.append(word)
            current_line_width += word_width
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_line_width = word_width

            # 매우 긴 단어 처리 (간단하게 다음 줄로 넘김)
            while current_line_width > max_width:
                if len(current_line[0]) == 1:
                    break
                lines.append(" ".join(current_line))
                current_line = []
                current_line_width = 0
                break

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def create_multiline_text_image(
    text_lines: List[str],
    font_path: str,
    font_size: int,
    output_filename: str,
    line_spacing: int = 10,
) -> None:
    """
    여러 줄의 텍스트를 이미지로 생성합니다.

    Args:
        text_lines: 이미지로 변환할 텍스트 줄들의 리스트.
        font_path: 사용할 .ttf 폰트 파일의 경로.
        font_size: 폰트 크기.
        output_filename: 생성될 이미지 파일의 이름.
        line_spacing: 줄 간 간격(픽셀).
    """
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Error: Font file not found or could not be opened at {font_path}")
        return

    # 각 줄의 크기 계산
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    max_line_width = 0
    total_text_height = 0
    line_heights: List[int] = []

    for line in text_lines:
        left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
        line_width = right - left
        line_height = bottom - top
        max_line_width = max(max_line_width, line_width)
        line_heights.append(line_height)
        total_text_height += line_height

    padding = 30
    image_width = max(max_line_width + 2 * padding, 100)
    image_height = max(
        total_text_height + (len(text_lines) - 1) * line_spacing + 2 * padding, 100
    )

    image = Image.new("RGB", (image_width, image_height), color="white")
    draw = ImageDraw.Draw(image)

    current_y = padding
    for i, line in enumerate(text_lines):
        draw.text((padding, current_y), line, font=font, fill="black")
        current_y += line_heights[i] + line_spacing

    image.save(output_filename)


@click.command()
@click.option(
    "--text",
    default="""ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz
0123456789 `~!@#$%^&*()-=_+\|<>,.;:/?\"'[{]}
별 헤는 밤, 낡은 짚차를 타고 숲 속으로, 퀘퀘한 향내를 맡으니 즈믄 강은 흐르고 저편에는 붉은 탑이 솟아있네.""",
    help="Input text for image generation",
)
@click.option("--font_size", default=20, type=int, help="Font size in pixels")
@click.option(
    "--output_base_name", default="image", type=str, help="Base name for output files"
)
@click.option(
    "--line_spacing", default=10, type=int, help="Line spacing between text lines"
)
def main(text: str, font_size: int, output_base_name: str, line_spacing: int) -> None:
    """
    TTF 폰트 기반 텍스트 이미지 생성기
    """
    output_folder = "data/output"
    docker_output_dir = os.path.join("/app", output_folder)
    os.makedirs(docker_output_dir, exist_ok=True)

    docker_fonts_dir = os.path.join("/app", "data/fonts")
    font_files = [f for f in os.listdir(docker_fonts_dir) if f.endswith(".ttf")]

    if not font_files:
        print(f"Error: No .ttf files found in {docker_fonts_dir}")
        return

    max_image_width = 800

    for font_file_name in font_files:
        full_font_path = os.path.join(docker_fonts_dir, font_file_name)
        try:
            current_font = ImageFont.truetype(full_font_path, font_size)
            text_with_font_name = add_font_name_line(full_font_path, text)
        except IOError:
            print(
                f"Skipping {font_file_name}: Font file not found or could not be opened."
            )
            continue

        wrapped_lines = wrap_text(
            text_with_font_name.strip(), current_font, max_image_width - 40
        )
        image_filename = f"{output_base_name}_{os.path.splitext(font_file_name)[0]}.png"
        output_image_path = os.path.join(docker_output_dir, image_filename)

        create_multiline_text_image(
            text_lines=wrapped_lines,
            font_path=full_font_path,
            font_size=font_size,
            output_filename=output_image_path,
            line_spacing=line_spacing,
        )

    print("All font renderings completed.")


if __name__ == "__main__":
    main()
