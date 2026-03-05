# Story - Vertical Slice: "First Night"

## Tone
Dark and serious. Mr. Robot, not Watch Dogs. The humor is dry, the stakes feel real, and the world doesn't hold your hand. When you find something disturbing in someone's files, the game doesn't celebrate - it just lets it sit there.

## The Player Character
A software developer who recently took a job at a company called **Nexus Solutions** and relocated to a new city. They're tech-literate (comfortable with a terminal, understands networking concepts) but they're not a hacker. They've never broken into a system. They're about to have a reason to start.

## Setting
The player just moved into **Greenvale Apartments**, a mid-rise building in a quiet part of the city. Something feels slightly off - the rent was suspiciously cheap, the building manager was eager to fill the unit, and the previous tenant left without notice.

---

## Beat 1 - Welcome Home (4 min)
Player arrives at their apartment for the first night. Boxes everywhere, barely unpacked.

*Real world tutorial*: The game teaches movement (WASD), interacting with objects (E). The player walks around the apartment - bedroom, living room, small office. They can examine boxes, look out the window, interact with a few things to get comfortable with the controls.

In the office, the player sits down at the desk and opens their laptop (interact with desk).

*Virtual world tutorial*: The OS boots up. The game walks the player through the desktop - clicking icons, opening windows, dragging/closing them, using the taskbar. The player opens the file browser, looks around their home directory. Then opens the terminal.

*Terminal tutorial*: The player learns basic commands one at a time:
- `pwd` - where you are
- `ls` - what's here
- `cd` - move around
- `cat` - read files
- `clear` - clean up
- `ifconfig` - see your network info

Each command is introduced naturally (e.g., "Check your network configuration with `ifconfig` to make sure your connection is set up properly").

The last tutorial prompt: *"Everything looks good. Run `netstat` to verify your active connections."*

The player types `netstat`. The output:

```
Active connections:
  Local             Remote              State
  192.168.1.100     192.168.1.1:443     ESTABLISHED    (gateway - normal)
  192.168.1.100     10.0.0.1:8443       ESTABLISHED    (??? - unknown)
```

The tutorial UI vanishes. No more hand-holding. No cheerful prompts. Just the player and that second connection that shouldn't be there. `10.0.0.1` - something on this network is mirroring their traffic. On their very first night.

---

## Beat 2 - The Neighbor (2 min)
The player closes the laptop. A knock at the door. It's **Alex Marin**, the neighbor from across the hall. Introducing himself, being friendly - he saw the moving truck earlier.

Alex is a **freelance journalist**. Not a hacker, not technical. Just a guy working on a story. Dialogue options:

- Ask about the building: *"It's... fine. Quiet. People keep to themselves mostly."*
- Ask about the wifi / internet: Alex pauses. *"Yeah, it's been weird lately. Slow at random times. I figured it was just the building's cheap infrastructure but... I don't know. Sometimes my laptop does stuff I didn't tell it to do. Files I don't remember downloading."* He shrugs it off, but he's clearly unsettled.
- Ask about the previous tenant: *"Left in a hurry from what I heard. Building manager didn't say much. Happens more than you'd think in this place."*

Alex is not suspicious of the network in a technical way - he doesn't know what a proxy is. He just knows something feels off. He leaves.

---

## Beat 3 - The Message (1 min)
Player goes back to the laptop. When they open the terminal, there's a new line that wasn't there before:

```
[UNKNOWN] > I see you found the second connection.
[UNKNOWN] > Don't panic. Don't disconnect it - they'll know you noticed.
[UNKNOWN] > You want answers? Start with the building router. 192.168.1.1.
[UNKNOWN] > Two ways in: the cafe downstairs has what you need for the easy way.
[UNKNOWN] >              the hard way - the firmware is NexOS 4.2. It has a known auth bypass. Look it up.
[UNKNOWN] > Check /var/log/auth.log once you're inside. You'll understand.
[UNKNOWN] > Good luck. We'll talk again.
```

Someone typed this into the player's terminal remotely. Someone who has access to their machine already. Someone who *wanted* them to see this.

The player has no idea who this is. But they have two leads.

---

## Beat 4 - Two Paths to the Router

The player needs to get into the building router at `192.168.1.1`. Two ways:

### Path A - The Cafe (credentials)
Player goes downstairs to the ground-floor cafe. There's a **public terminal** in the corner. The barista barely looks up.

On the cafe terminal, the player finds:
- A **building notice board app** with maintenance schedules. One entry: *"Network maintenance - DO NOT reset router"* signed by a "V. Kuznetsov" - a name that doesn't appear anywhere else in building communications.
- A **browser with cached pages** - a forum post by someone asking about Greenvale Apartments: *"Does anyone know why the turnover rate is so high in that building?"* The replies are [deleted].
- In the terminal's temp files (`/tmp/`): a plaintext file `router_setup_notes.txt` with the building router's admin credentials left behind by whoever configured it: `admin / Nexus_GV_2024`

The player SSHs into the router: `ssh admin@192.168.1.1`

### Path B - The Exploit (vulnerability)
The player investigates the router from their laptop. `probe 192.168.1.1` reveals the firmware: `NexOS 4.2.1-build.7734`. The unknown messenger said this version has a known auth bypass.

The player checks their own system - in `/home/player/tools/` there's an exploit database file (a text file listing known vulnerabilities). Searching for NexOS 4.2 reveals: *"CVE-2024-31337: NexOS <= 4.2.3 - authentication bypass via malformed SSH handshake. Use: `exploit ssh-bypass 192.168.1.1`"*

The player runs the exploit. A mini-game puzzle (sequence-based - the player must send packets in the right order based on the CVE description). On success, they're dropped into a shell on the router.

Both paths lead to the same place: a root shell on `192.168.1.1`.

---

## Beat 5 - Inside the Router (3 min)
This is the first real "hack" - whether through stolen creds or an exploit, the player has crossed a line for the first time. They're inside a system that isn't theirs.

Inside the router's filesystem:
- `/var/log/auth.log` shows **dozens of SSH sessions** from `10.0.0.1` to every device in the building, at all hours. Whoever controls that proxy has been logging into tenants' machines regularly.
- `/etc/nexus/` - a directory that shouldn't exist on a consumer router. Configuration files for a **traffic mirroring system** called `PRISM-L`. Every tenant's traffic is being copied to `10.0.0.1`. Every keystroke, every website, every file download.
- `/etc/nexus/prism.conf` contains `tripwire_mode = active` with a list of `watch` rules - specific file paths and commands that trigger alerts if accessed. The player is reading files on this list *right now*.
- `/etc/nexus/tenants.db` - an encrypted file. Decrypting it (mini-game puzzle: a substitution cipher, with the key clued from strings in the config files) reveals a **dossier on every current and former tenant**. Notes next to each name. The player's entry: `"Priority target. Placement confirmed. Monitoring active."`

The player didn't stumble onto this. **They were placed in this building deliberately.** Their new job at Nexus, the cheap rent, the fast approval - it was all arranged.

A notification appears:
```
CONNECTION TO 192.168.1.1 TERMINATED
ROUTING TABLE CHANGED
```

The tripwire fired. The player is kicked out. The system knows someone accessed the PRISM-L files. And the tripwire doesn't just flag the intruder - it triggers a **full network audit**, scanning every device on the LAN for anomalies.

Alex - who is not a hacker but has been saving files, screenshots, and notes about the building's strange patterns onto his own machine for his journalism piece - just had all of that flagged. Downloaded floor plans. Photos of unfamiliar people entering the building at night. A half-written article. To someone reviewing the audit, it looks like Alex has been building a case. Because he has. He just didn't know the full scope of what he was up against.

The player closes the laptop. It's late. Nothing they can do right now. They go to sleep.

---

## Beat 6 - Gone (2 min)
The player wakes up. Morning light. Everything seems normal for a moment.

They step into the hallway. Alex's door is **ajar**. That's wrong.

Inside: laptop still open, screen on, chair pushed back. Coffee on the desk - stone cold, left from last night. A single line typed in Alex's terminal, never sent:

```
they know about the
```

Alex is gone.

On Alex's still-open laptop, one browser tab is visible: an unfinished article draft titled **"Nexus Solutions and the Greenvale Surveillance Program: How a Tech Company Turned an Apartment Building Into a Panopticon."**

Alex wasn't a hacker. He was a journalist who noticed strange things and started keeping notes. He was doing his job. And the player - on their very first night, with their very first hack - triggered the audit that exposed him.

They came in the night. While the player slept.

---

## End State

The player now knows:
- Their employer is running a covert surveillance operation on this building
- They were specifically placed here as a "priority target" - but they don't know why yet
- A journalist investigating this was taken **because the player's hack triggered a network audit that flagged his research**
- An unknown hacker contacted them and seems to want to help - but who are they and why?
- The player slept through it. They didn't hear a thing. That's maybe the most unsettling part.
- Everything the player does on this network from now on has consequences for real people

---

## Why This Story Works for a Hacking Game
- **The tutorial IS the story.** Learning commands isn't busywork - it ends with the discovery that kicks off everything. The `netstat` moment is the inciting incident.
- **Every hack has consequences.** Your very first real hack gets a journalist disappeared. The game teaches you immediately: actions on a network are not abstract. Real people get hurt.
- **Two paths reward different playstyles.** Social/exploration players find the credentials in the cafe. Technical players exploit the vulnerability. Both work, both feel earned.
- **Every hack is motivated.** You're not hacking for fun - someone is spying on you and you need to know why.
- **Escalating discoveries.** Rogue connection -> building-wide surveillance -> your name on a target list -> your entire life was arranged. Each layer is worse than the last.
- **The hacking IS the storytelling.** The biggest reveals come from reading log files, decrypting databases, and finding things in file systems. Not from cutscenes.
- **Guilt as a narrative engine.** Alex wasn't a hacker. He was a journalist keeping notes. The player's clumsy first hack got him caught. Finding Alex (or finding out what happened to him) becomes a personal obligation.
- **The unknown hacker is a hook.** Who contacted the player? How do they have access to the player's machine? Are they an ally or are they manipulating the player into doing exactly what just happened? This thread carries the whole game.
- **Sets up the full game.** Who is behind PRISM-L? Why is the player a "priority target"? What happened to Alex? What is Nexus really doing? Who is the unknown hacker? What was the previous tenant investigating? Can the player learn to operate without leaving collateral damage?