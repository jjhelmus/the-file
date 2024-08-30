import io
import os
import tempfile
import zipfile

import pandas as pd


def zip_playload() -> bytes:
    zip_contents = """name,score
    Mario,267
    Luigi,187
    Bowser,304
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as zf:
        zf.writestr("data.csv", zip_contents)
    buffer.seek(0)
    return buffer.read()


def hdf_payload() -> bytes:
    df = pd.DataFrame([["Mario", 519], ["Luigi", 202], ["Toad", 308]], columns=['name', 'score'])
    with tempfile.TemporaryDirectory() as tmpdirname:
        h5_file = os.path.join(tmpdirname, "data.h5")
        df.to_hdf(h5_file, key='data')
        with open(h5_file, mode="rb") as fh:
            hdf_bytes = fh.read()
    return hdf_bytes


def html_payload() -> bytes:
    df = pd.DataFrame([["Mario", 125], ["Luigi", 987], ["Peach", 212]], columns=['name', 'score'])
    html_str = df.to_html()
    return html_str.encode("utf-8")


def create_the_file(filename: str) -> None:
    hdf5_offset = 512  # 1024, 2048, etc are also allowed
    with open(filename, mode="wb") as out:
        # start the file with a HTML table
        out.write(html_payload())
        # fill to the offset to before the HDF5 file
        out.write(b"\n" * (hdf5_offset - out.tell()))
        # add content to make a valid HDF5 file, these can start at an offset of 512, 1024, 2048, ...
        out.write(hdf_payload())
        # Zip files are detected from the end of the file, so end with a zipped CSV file
        out.write(zip_playload())


def read_the_file(filename: str) -> None:
    zip_df = pd.read_csv(filename)
    print("Zip:\n", zip_df)
    hdf_df = pd.read_hdf(filename)
    print("HDF:\n", hdf_df)
    html_df = pd.read_html(filename)
    print("HTML:\n", html_df)


if __name__ == "__main__":
    filename = "results.csv.zip"
    create_the_file(filename)
    read_the_file(filename)
