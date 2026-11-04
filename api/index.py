from http.server import BaseHTTPRequestHandler
import json
import random


def conflicts(board):
    count = 0
    n = len(board)

    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                count += 1

    return count


def solve_n_queens(n):
    best_board = None
    frames = []

    for restart in range(100):
        board = [random.randrange(n) for _ in range(n)]
        frames.append(board[:])

        for step in range(1000):
            current = conflicts(board)

            if current == 0:
                return {
                    "solved": True,
                    "frames": frames,
                    "moves": step,
                    "restarts": restart
                }

            best_moves = []
            best_score = current

            for col in range(n):
                old_row = board[col]

                for row in range(n):
                    if row == old_row:
                        continue

                    board[col] = row
                    score = conflicts(board)

                    if score < best_score:
                        best_score = score
                        best_moves = [(col, row)]
                    elif score == best_score and score < current:
                        best_moves.append((col, row))

                board[col] = old_row

            if not best_moves:
                break

            col, row = random.choice(best_moves)
            board[col] = row
            frames.append(board[:])

        if best_board is None or conflicts(board) < conflicts(best_board):
            best_board = board[:]

    return {
        "solved": False,
        "frames": frames,
        "moves": len(frames),
        "restarts": 100
    }


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")

            n = int(data.get("n", 8))

            if n < 4 or n > 12:
                raise ValueError("N must be between 4 and 12")

            result = solve_n_queens(n)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as error:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(error)}).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"message":"N-Queen API is running"}')
