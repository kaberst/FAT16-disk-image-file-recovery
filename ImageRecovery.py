import os
import random
import shutil
import struct
class FAT:
    def getSector(self, sector: int) -> bytes:
        self.fatFile.seek(sector * self.BytsPerSec)
        return self.fatFile.read(self.BytsPerSec)

    def __init__(self, imageFileName: str) -> None:
        self.fatFile = open(imageFileName, 'rb')
        self.BytsPerSec = 512  # We assume 512 bytes until we know better
        block0 = self.getSector(0)  # Read metadata from the first sector

        # Unpack filesystem metadata
        self.jmpBoot, self.OemName, self.BytsPerSec, self.SecPerClus, \
        self.ResvdSecCnt, self.NumFATs, self.RootEntCnt, \
        self.TotSec16, self.Media, self.FATSz16, self.SecPerTrk, \
        self.NumHeads, self.HiddSec, self.TotSec32, self.FATSz32 = \
            struct.unpack('<3s8sHBHBHHBHHHLLL', block0[:40])

        self.RootDirSectors = int(
            (self.RootEntCnt * 32 + self.BytsPerSec - 1) / self.BytsPerSec)
        self.FirstDataSector = self.ResvdSecCnt + (
                self.NumFATs * self.FATSz16) + self.RootDirSectors
        self.DataSec = self.TotSec32 - (self.ResvdSecCnt +
                                        (self.NumFATs * self.FATSz32) + self.RootDirSectors)
        self.CountOfClusters = int(self.DataSec / self.SecPerClus)
        self.FATStart = self.ResvdSecCnt
        self.RootDirStart = self.ResvdSecCnt + self.NumFATs * self.FATSz16

    def __str__(self) -> str:
        return f'\n{self.BytsPerSec=} bytes\n{self.SecPerClus=}' \
               f'sectors\n{self.ResvdSecCnt=} sectors\n{self.NumFATs=}\n' \
               f'{self.RootEntCnt=} entries\n{self.TotSec32=} sectors\n' \
               f'{self.FATSz32=} sectors\n{self.HiddSec=} sectors\n\n'

    def close(self) -> None:
        self.fatFile.close()


def recover_content_from_disc_image(image_path, output_dir):
    fat_instance = None  # Initialize fat_instance to None
    try:
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
                
        # Create an instance of the FAT class
        fat_instance = FAT(image_path)

        # Access file system information using the FAT instance
        print(fat_instance)

        with open(image_path, 'rb') as input_file:
            # Read the content of the disc image
            data = input_file.read()

            # Construct the output directory path
            output_dir_path = os.path.join(output_dir, "RecoveredFiles")
            os.makedirs(output_dir_path, exist_ok=True)

            # Calculate the number of files based on a fixed cluster size
            cluster_size = 131048  # Change this based on your actual cluster size
            num_files = len(data) // cluster_size

            directories = []

            # Recover directories and files from the disc image
            
            for i in range(num_files):
                Directory_name = f"DIR{i + 1:04d}"
                item_path = os.path.join(output_dir_path, Directory_name)

                # Detect and recover directories
                if some_condition_to_identify_directories(data[i * cluster_size: (i + 1) * cluster_size]):
                    directories.append(item_path)
                    os.makedirs(item_path, exist_ok=True)
                    print(f"Directory recovered: {item_path}")
                    # Shuffle the order of recovered files
                    shuffled_files = random.sample(range(num_files), num_files)

                    # Write recovered .BIN and .TXT files to the output directory
                    for j in shuffled_files:
                        bin_file_name = f"FILE{j + 1:04d}.BIN"
                        txt_file_name = f"FILE{j + 1:04d}.TXT"

                        bin_file_path = os.path.join(item_path, bin_file_name)
                        txt_file_path = os.path.join(item_path, txt_file_name)

                        # Write a cluster-sized chunk to each .BIN file
                        with open(bin_file_path, 'wb') as bin_output_file:
                            bin_output_file.write(data[j * cluster_size: (j + 1) * cluster_size])

                        # Trim the .BIN file to correct length and save as .TXT
                        with open(txt_file_path, 'wb') as txt_output_file:
                            txt_output_file.write(data[j * cluster_size: (j + 1) * cluster_size].rstrip(b'\x00'))

                        print(f"File recovered: {bin_file_path}")
                        print(f"File recovered: {txt_file_path}")

                

            # Write recovered .BIN and .TXT files to the output directory
            for i in range(num_files):
                bin_file_name = f"FILE{i + 1:04d}.BIN"
                txt_file_name = f"FILE{i + 1:04d}.TXT"

                bin_file_path = os.path.join(output_dir_path, bin_file_name)
                txt_file_path = os.path.join(output_dir_path, txt_file_name)

                # Write a cluster-sized chunk to each .BIN file
                with open(bin_file_path, 'wb') as bin_output_file:
                    bin_output_file.write(data[i * cluster_size: (i + 1) * cluster_size])

                # Trim the .BIN file to correct length and save as .TXT
                with open(txt_file_path, 'wb') as txt_output_file:
                    txt_output_file.write(data[i * cluster_size: (i + 1) * cluster_size].rstrip(b'\x00'))

                print(f"File recovered: {bin_file_path}")
                print(f"File recovered: {txt_file_path}")

            # Create a directory for good files
            good_files_dir = os.path.join(output_dir, "GoodFiles")
            os.makedirs(good_files_dir, exist_ok=True)

            # Create a listing.txt file to store the list of directories and files
            listing_file_path = os.path.join(good_files_dir, "listing.txt")
            with open(listing_file_path, 'w') as listing_file:
                # Write the list of directories to listing.txt
                listing_file.write("List of Directories:\n")
                for directory in directories:
                    listing_file.write(f"{directory}\n")

                # Write the list of recovered files to listing.txt
                listing_file.write("\nList of Recovered Files:\n")
                for i in range(num_files):
                    bin_file_name = f"FILE{i + 1:04d}.BIN"
                    txt_file_name = f"FILE{i + 1:04d}.TXT"

                    bin_file_path = os.path.join(output_dir_path, bin_file_name)
                    txt_file_path = os.path.join(output_dir_path, txt_file_name)

                    listing_file.write(f"{bin_file_path}\n")
                    listing_file.write(f"{txt_file_path}\n")

            # Create a filename_with_length.txt file to store the names, lengths, and directories of recovered files
            filename_with_length_path = os.path.join(good_files_dir, "filename_with_length.txt")
            with open(filename_with_length_path, 'w') as filename_with_length_file:
                # Write the names, lengths, and directories of recovered files to filename_with_length.txt
                for i in range(num_files):
                    dir_file_name = f"DIR{i + 1:04d}"
                    bin_file_name = f"FILE{i + 1:04d}.BIN"
                    txt_file_name = f"FILE{i + 1:04d}.TXT"

                    bin_file_path = os.path.join(output_dir_path, bin_file_name)
                    txt_file_path = os.path.join(output_dir_path, txt_file_name)
                    dir_file_path = os.path.join(output_dir_path, dir_file_name)

                    filename_with_length_file.write(f"File: {bin_file_path}, Length: {os.path.getsize(bin_file_path)} bytes\n")
                    filename_with_length_file.write(f"File: {txt_file_path}, Length: {os.path.getsize(txt_file_path)} bytes\n")
                    # Walk through all the directories and files
                    total_size=0
                    for dirpath, dirnames, filenames in os.walk(dir_file_path):
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            total_size += os.path.getsize(filepath)
                            
                    filename_with_length_file.write(f"File: {dir_file_path}, Length:{total_size} bytes \n")

            # Identify unlinked files (files not part of a recovered directory)
            unlinked_files_dir = os.path.join(output_dir, "UnlinkedFiles")
            os.makedirs(unlinked_files_dir, exist_ok=True)
             
# Move unlinked files to the UnlinkedFiles directory
            for item in os.listdir(output_dir_path):
                item_path1=os.path.join(output_dir_path,item)
                # Check if it's a file
                if os.path.isfile(item_path1):
                    dest_path = os.path.join(unlinked_files_dir, item)
                    # Copy the file to the destination folder
                    shutil.copy2(item_path1, dest_path)
                    print(f"File moved to UnlinkedFiles: {dest_path}")

            print(f"Content successfully recovered and saved to {output_dir_path}")
            #print(f"Number of files on the disk: {num_files}")
            print(fat_instance)

    except Exception as e:
        print(f"Error recovering content: {e}")

def some_condition_to_identify_directories(data_chunk):
    # Example condition for FAT: Check the attributes in the directory entry
    # Modify this condition based on the actual structure of the disk image

    # Offset 11 in the directory entry typically contains attributes
    attributes_byte = data_chunk[11]

    # Check if the attributes byte indicates a directory
    return attributes_byte & 0x10 != 0

if __name__ == "__main__":
    disc_image_path = "project.img"
    output_content_dir = "RecoveredData"

    recover_content_from_disc_image(disc_image_path, output_content_dir)

