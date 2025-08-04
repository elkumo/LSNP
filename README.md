# LSNP
Local Social Networking Protocol (LSNP) Machine Project requirement for the course CSNETWK

## How to run
1. Create a 'USER.csv' file. Refer to the sample file in /Sample/USER.csv'
   - The file should contain user data in the format:

|    my_user_id    | display_name |
|:----------------:|:------------:|
| user@192.168.0.1 |     user     |
2. Run the 'main.py' file via your terminal or command prompt:
   ```bash
   python main.py
   ```
3. ***OPTIONAL***: If you want to run the program in verbose mode:
   ```bash
   python main.py --verbose
   ```
   
## Requirements
- Python 3.8 or higher
- Required libraries: **NONE**

## Functionality
### Milestone 1
- [x] Clean Architecture & Logging
- [x] Protocol Compliance Test Suite
- [x] Message Sending and Receiving
- [x] Protocol Parsing and Message Format

### Milestone 2
- [x] User Discovery and Presence
- [x] Messaging Functionality

### Milestone 3
- [ ] Profile Picture and Likes
- [ ] File Transfer
- [ ] Token Handling and Scope Validation
- [ ] Group Management
- [ ] Game Support (Tic Tac Toe)

## AI Usage
AI was used to generate the intial project structure, parsing logic, and some of the protocol compliance test cases. It also assisted in generating documentation and comments throughout the codebase.

## Credits
- [@elkumo](https://github.com/elkumo)
- [@ixelated](https://github.com/ixelated)

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/elkumo/LSNP/blob/main/LICENSE.md) file for details