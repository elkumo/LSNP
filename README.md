# LSNP (Group 8)
Group 8's Local Social Networking Protocol (LSNP) Machine Project requirement for the course CSNETWK. This program allows users to communicate over a local network. Features such as messaging, group management, user discovery, token validation, status updates, a tictactoe game, and verbose logging are implemented.

## How To Run
1. Create a 'USER.csv' file. Refer to the sample file in [/Sample/USER.csv](https://github.com/elkumo/LSNP/blob/main/Sample/sample_USER.csv)
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
- [ ] ~~Profile Picture and Likes~~
- [ ] ~~File Transfer~~
- [x] Token Handling and Scope Validation
- [x] Group Management
- [x] Game Support (Tic Tac Toe)

## AI Usage
AI was used to generate the intial project structure, parsing logic, and some of the protocol compliance test cases. It also assisted in generating documentation and comments throughout the codebase. Debugging and troubleshooting were done manually, with AI providing suggestions for potential fixes.

## Credits
- [@elkumo](https://github.com/elkumo) - Elmo Mandigma
- [@ixelated](https://github.com/ixelated) - Alexi Alberto

## Task Contribution:
| Task / Role                             | Mandigma  | Alberto   |
|-----------------------------------------|-----------|-----------|
| **Network Communication**               |           |           |
| UDP Socket Setup                        | Primary   | Secondary |
| mDNS Discovery Integration              | Secondary | Primary   |
| IP Address Logging                      | Primary   | Secondary |
| **Core Feature Implementation**         |           |           |
| Core Messaging (POST, DM, LIKE, FOLLOW) | Primary   | Secondary |
| File Transfer (Offer, Chunk, ACK)       | Secondary | Primary   |
| Tic Tac Toe Game (with recovery)        | Secondary | Primary   |
| Group Creation / Messaging              | Primary   | Secondary |
| Induced Packet Loss (Game & File)       | Secondary | Primary   |
| Acknowledgement / Retry                 | Secondary | Primary   |
| **UI & Logging**                        |           |           |
| Verbose Mode Support                    | Primary   | Secondary |
| Terminal Grid Display                   | Secondary | Primary   |
| Message Parsing & Debug Output          | Secondary | Primary   |
| **Testing and Validation**              |           |           |
| Inter-group Testing                     | Secondary | Primary   |
| Correct Parsing Validation              | Primary   | Secondary |
| Token Expiry & IP Match                 | Primary   | Secondary |
| **Documentation & Coordination**        |           |           |
| RFC & Project Report                    | Primary   | Secondary |
| Milestone Tracking & Deliverables       | Primary   | Secondary |

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/elkumo/LSNP/blob/main/LICENSE.md) file for details