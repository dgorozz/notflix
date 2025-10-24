import cmd
import requests
import sys

API_URL = "http://localhost:8000"

BLUE_COLOR = "\033[94m"
RESET_COLOR = "\033[0m"


class NotflixCLI(cmd.Cmd):
    intro = "\n🎬 Welcome to Notflix CLI. Write 'help' or '?' to see available commands.\n"
    prompt = f"{BLUE_COLOR}notflix> {RESET_COLOR}"

    # ----------------------------
    # COMANDOS DE SHOWS
    # ----------------------------
    def do_show(self, arg):
        """
        show list               -> get show list
        show <show_id> info     -> get show info
        show <show_id> start    -> start show
        """

        tokens = arg.strip().split()
        if not tokens:
            print("Not valid format")
            print(self.do_show.__doc__)
            return
        
        if not tokens[0].isdigit():
            if tokens[0] == "list":

                r = requests.get(f"{API_URL}/shows")

                if r.status_code != 200:
                    print("Error:", r.text)
                
                for show in r.json():
                    print(f"{show['id']}: {show['name']} ({show['gender']})")
            else:
                print(f"Unknown action: {tokens[0]}")
                print(self.do_show.__doc__)

            return
        
        if len(tokens) < 2:
            print("Not valid format")
            print(self.do_show.__doc__)
            return
        
        show_id = int(tokens[0])
        action = tokens[1]

        if action == "info":

            r = requests.get(f"{API_URL}/shows/{show_id}")

            if r.status_code != 200:
                print("Show not found in catalog")
                return
            
            show = r.json()
            print(f"\n{show['name']}")
            print(f"Description: {show['description']}")
            print(f"Gender: {show['gender']}")
            print(f"Seasons: {len(show['episodes'])} {show['episodes']}\n")

        elif action == "start":

            r = requests.post(f"{API_URL}/shows/{show_id}/start")

            if r.status_code != 200:
                print("Error:", r.text)
                return
            
            data = r.json()
            print(f"Session initialized (id={data['id']}) for {data['show']['name']}")
            print(f"Starting on season {data['season']}, episode {data['episode']}")

        else:
            print(f"Unknown action: {action}")
            print(self.do_show.__doc__)

        return

    def do_session(self, arg):
        """
        session list <finished|watching?>   -> list all session with optional filter
        session <session_id> info           -> session info
        session <session_id> delete         -> delete session
        session <session_id> next           -> next episode
        session <session_id> previous       -> previous episode
        session <session_id> restart        -> restart show
        session <session_id> goto <season> <episode> -> go to specific episode
        """
        
        tokens = arg.strip().split()
        if not tokens:
            print("Not valid format")
            print(self.do_show.__doc__)
            return
        
        if not tokens[0].isdigit():

            if tokens[0] == "list":

                state = None
                if len(tokens) > 1 and tokens[1] in {"finished", "watching"}:
                    state = tokens[1]

                r = requests.get(f"{API_URL}/sessions", params={"state": state} if state else {})
                if r.status_code != 200:
                    print("Error:", r.text)
                    return
                
                data = r.json()
                if not data:
                    print("No sessions")
                    return
                
                for session in data:
                    print(f"{session['id']} | {session['show']['name']} | S{session['season']}E{session['episode']} | {session['state']}")
                
            else:
                print("Not valid format")
                print(self.do_session.__doc__)
            
            return
        
        session_id = tokens[0]
        action = tokens[1]

        if action == "info":
            r = requests.get(f"{API_URL}/sessions/{session_id}")

            if r.status_code == 404:
                print("That session does not exists!")
                return
            elif r.status_code != 200:
                print("Error:", r.text)
                return
            
            session = r.json()
            print("\nSession ID:", session["id"])
            print("Show id:", session["show_id"])
            print("State:", session["state"])
            print("Season:", session["season"])
            print("Episode:", session["episode"])
            print("Started at:", session["start_date"])
            print("Finished at:", session["end_date"], "\n")

        elif action == "next":
            r = requests.post(f"{API_URL}/sessions/{session_id}/next")

            if r.status_code == 400:
                print("Show already finished! Restart session to watch again")
                return
            elif r.status_code != 200:
                print("Error:", r.text)
                return
            
            session = r.json()
            if session["state"] == "watching":
                print(f"Episode watched. Next again to watch S{session['season']}E{session['episode']}")
            else:
                print(f"Episode watched. Show finished, congratulations!!")
        
        elif action == "previous":
            r = requests.post(f"{API_URL}/sessions/{session_id}/previous")

            if r.status_code == 400:
                print("Show already finished or this is the first episode and you can't go further!")
                return
            elif r.status_code != 200:
                print("Error:", r.text)
                return
            
            session = r.json()
            print(f"Moved back one episode to S{session['season']}E{session['episode']}")

        elif action == "restart":
            r = requests.post(f"{API_URL}/sessions/{session_id}/restart")

            if r.status_code == 404:
                print("Session does not exists!")
                return
            elif r.status_code != 200:
                print("Error:", r.text)
                return
            
            session = r.json()
            print(f"Restarted to S{session['season']}E{session['episode']}")
        
        elif action == "goto":

            if len(tokens[2:]) != 2:
                print("Not valid format")
                print(self.do_session.__doc__)
                return
            
            season, episode = tokens[2:]

            r = requests.post(f"{API_URL}/sessions/{session_id}/goto", json={"season": season, "episode": episode})

            if r.status_code == 400:
                print("Show already finished! Restart session to watch again")
                return
            elif r.status_code == 404:
                print(f"S{season}E{episode} not found")
                return
            elif r.status_code != 200:
                print("Error:", r.text)
                return
            
            session = r.json()
            print(f"Moved to S{session['season']}E{session['episode']}")
        
        elif action == "delete":

            r = requests.delete(f"{API_URL}/sessions/{session_id}")

            if r.status_code == 404:
                print(f"That session does not exists!")
                return
            elif r.status_code != 204:
                print("Error:", r.text)
                return

            print(f"Session removed succesfully!")

        else:
            print(f"Unknown action: {action}")

        return

    def emptyline(self):
        pass


if __name__ == "__main__":
    NotflixCLI().cmdloop()