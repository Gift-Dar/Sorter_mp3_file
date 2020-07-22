# -*- coding utf-8 -*-
from collections import namedtuple
import click
import os
import tinytag


def remove_forbidden_char_from_str(name_str):
    """Функция для удаления из тэгов запрещенных символов"""
    char_list = ['\\', '/', ':', '*', '?', '<', '>', '|', '\"', '\'']
    for elem in char_list:
        name_str = name_str.replace(elem, ' ')
    return name_str.strip()


Song = namedtuple('Song', 'Old_name, Old_path, New_name, Dst_path')


def form_list_songs_from_srcdir(src_dir, dst_dir):
    """Формирует список объектов Song, исходя из необходимого набора тэгов и прав на запись/чтение файлов, """
    """нахдящихся в переданной директории (src_dir)"""
    songs = []
    for file in os.listdir(src_dir):
        if file.endswith(".mp3"):
            try:
                tag = tinytag.TinyTag.get(os.path.join(src_dir, file))
                """Проверка, что тэги не None, и не заполнены одними пробелами"""
                if (tag.album is not None and tag.artist is not None) and \
                        (tag.album.strip() and tag.artist.strip()):
                    """Формирование нового имени"""
                    if tag.title.strip():
                        new_name = f'{tag.title.strip()} - {tag.artist.strip()} - {tag.album.strip()}.mp3'
                    else:
                        new_name = file
                    """Формирование нового пути"""
                    dst_path = os.path.join(
                        dst_dir,
                        remove_forbidden_char_from_str(tag.artist),
                        remove_forbidden_char_from_str(tag.album),
                        remove_forbidden_char_from_str(new_name)
                    )
                    """Создание объекта Song, добавление его к списку"""
                    list_tags = [file, os.path.join(src_dir, file), remove_forbidden_char_from_str(new_name), dst_path]
                    songs.append(Song._make(list_tags))
                else:
                    continue
            except PermissionError:
                print(f'Отсутствуют необходимые права для чтения или изменения файла: {file}.'
                      f'Файл останется в исходной директории.')
        else:
            continue
    return songs


@click.command()
@click.option('-s', '--src-dir', default=os.getcwd(), help='Source directory')
@click.option('-d', '--dst-dir', default=os.getcwd(), help='Destination directory')
def main(src_dir, dst_dir):
    if os.path.exists(src_dir):
        songs = form_list_songs_from_srcdir(src_dir, dst_dir)
        for elem in songs:
            """Поэлементное перемещение объектов по заданному пути"""
            try:
                os.replace(elem.Old_path, elem.Dst_path)
            except FileNotFoundError:
                os.renames(elem.Old_path, elem.Dst_path)
            except PermissionError:
                print(f'Отсутствуют необходимые права для записи файла "{elem.Old_name}", \nпуть: {elem.Dst_path}.\n'
                      f'Файл останется в исходной директории.')
                continue
            print(f'{os.path.relpath(elem.Old_path, start=None)} -> {os.path.relpath(elem.Dst_path, start=None)} \n')
        print('Done')
    else:
        print(f'Указанная исходная директория: {src_dir}, не найдена. '
              f'Проверьте правильность указанного пути и попробуйте снова.')


if __name__ == "__main__":
    main()