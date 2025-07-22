from dmi_data import unzip_and_merge_dmi_obs_data, read_file_in_zip

df = unzip_and_merge_dmi_obs_data(
    "data/2023.zip",
    "txt",
    n_files=50
)

# df = read_file_in_zip(
#     "data/2023.zip",
#     "2023-01-01.txt"
# )

df.to_csv("data/parse_data_text.csv")