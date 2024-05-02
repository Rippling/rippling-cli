## Running the CLI

### Run using python
Run the following command:
```
python ./rippling_cli/cli/main.py
```
If the setup is complete, you should see the following output.
<details>
<summary>screenshot</summary>

![image](https://github.com/Rippling/rippling-cli/assets/88705494/32909c62-f0b4-429a-b288-1b0cbe82089e)
</details>

### Run using pyinstaller
- Install pyinstaller using the following command:
```
pip install pyinstaller
```
- Install the pyinstaller executable using the following command:
```
pyinstaller rippling_cli/cli/main.py --name rippling --noconfirm
```
- Run the executable using the following command:
```
./dist/rippling/rippling [your command here]
```
You can setup alias for the path of executable to run it from anywhere in the terminal.

### Run using homebrew 

Pre-requisites:
- Install the homebrew
- Generate the pyinstaller executable as mentioned above.


Steps:
- Create the tar file using pyinstaller executable.
```
tar -cvf rippling.0.1.0.tar dist/rippling
```
- Gzip the tar file using the below command
```
gzip rippling.0.1.0.tar
```
- Create a formula file rippling.rb in the current directory.
  - replace the url with the path of the tar file.
  - generate the sha256 of the tar file using the below command.
      ```
     shasum -a 256 rippling.0.1.0.tar.gz
      ```
```angular2html
class Rippling < Formula
  desc "Rippling CLI"
  homepage "https://github.com/Rippling/rippling-cli"
  url "file:///path/to/rippling-cli/rippling.0.1.0.tar.gz"
  sha256 "copy the sha256 of the tar file"

  def install
  	bin.install "rippling/_internal"
    bin.install "rippling/rippling"
  end
end
```
- Install the formula using the below command.
```
brew install rippling.rb
```
Now you can run the rippling command from anywhere in the terminal.