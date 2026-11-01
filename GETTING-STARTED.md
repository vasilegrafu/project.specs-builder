# Getting started

This guide takes you from nothing to your first product specification. You don't
need to know how to code. It takes about 20 minutes.

**What you'll need**

- A computer with Windows 10 (version 1809 or later), Windows 11, or macOS 13 or
  later. Linux works too; the commands are the macOS ones.
- A paid Claude plan: Pro, Max, Ultra, Team or Enterprise. The free plan doesn't
  include Claude Code. You only need this to *write* specifications.
- An internet connection.

**Two words you'll see**

- **Terminal:** a window where you type commands. On Windows it's called
  PowerShell or Terminal. You'll only need a few commands, all given here.
- **Specification** (or spec): the document that says what a product must do. This
  tool keeps it as a small website you open on your own computer.

## Step 1: Put this folder somewhere simple

If you received a `.zip` file, unpack it first: on Windows, right-click it and
choose **Extract All**. Nothing works from inside a zip.

Put the folder somewhere easy to find, such as your Documents folder.

## Step 2: Install Python

Python is the free program that runs the specification website.

**Windows**

1. Go to [python.org/downloads](https://www.python.org/downloads/) and download
   Python 3.14 or later.
2. Run the installer. If it offers an **Add python.exe to PATH** box, tick it
   before you continue. This is the step most often missed.

**macOS**

1. Go to [python.org/downloads](https://www.python.org/downloads/) and download
   Python 3.14 or later.
2. Open the file you downloaded, and follow the installer.

## Step 3: Install Claude Code

**1. Open a terminal.**

- Windows: press **Windows key + X**, then choose **Terminal** or **Windows
  PowerShell**.
- macOS: press **Cmd + Space**, type `Terminal`, and press Enter.

**2. Copy the line for your computer, paste it into the terminal, and press Enter.**

Windows:

```
irm https://claude.ai/install.ps1 | iex
```

macOS or Linux:

```
curl -fsSL https://claude.ai/install.sh | bash
```

It may show nothing for a while as it downloads. Wait until you see **Claude Code
successfully installed!**

**3. Close the terminal.** A new one is needed to pick up what you installed.

*Prefer not to use a terminal?* The Claude desktop app has a **Code** tab, and
there's an extension for VS Code. Both can open this folder. The rest of this guide
uses the terminal, but what you say to Claude is the same.

## Step 4: Check your setup

- **Windows:** open this folder and double-click **check-setup.cmd**. If Windows
  warns you about running it, choose **More info**, then **Run anyway**.
- **macOS:** open a terminal, type `sh ` (with a space after it), drag
  **check-setup.sh** from Finder into the terminal window, and press Enter.

You want to see **All good**. If something says **MISSING**, the line under it says
what to do. Fix it and run the check again.

## Step 5: Look at a finished example

This shows you what you'll be making, before you make one.

- **Windows:** double-click **open-example.cmd**.
- **macOS:** the same as step 4, using **open-example.sh**.

Your browser opens on **Voltline**, a made-up online shop. Try these:

- **Requirements**, in the top menu: pick one to read it. The small arrow beside
  each word opens its menu.
- **Prototype**: a working drawing of each screen.
- **Graph**: a map of how everything connects.
- Pause on any ID, such as `R4`, to see what kind of thing it is. Right-click it
  to see a card about it.

When you're done, close the black window. That stops the website.

## Step 6: Write your first specification

**1. Open a terminal in this folder.**

- Windows: open the folder in File Explorer, right-click an empty space, and choose
  **Open in Terminal**.
- macOS: open a terminal, type `cd ` (with a space after it), drag this folder into
  the window, and press Enter.

**2. Start Claude Code.** Type this and press Enter:

```
claude
```

The first time, your browser opens so you can sign in to your Claude account. Then
Claude Code asks whether you trust this folder. Say yes.

**3. Tell it what you want.** Always say `specs-builder-2`, so it uses this tool.
Pick whichever fits:

| You have | Say something like |
|---|---|
| An idea | Use specs-builder-2. Customers should be able to download their invoices as PDFs. |
| Only a rough goal | Use specs-builder-2 and ask me about a booking site for a dental clinic. |
| Something that already exists | Use specs-builder-2 to reverse-engineer the folder `C:\Projects\my-app`. |

Claude writes what it can, then asks what it needs to know. It will also ask for
permission before running commands. Read what it wants to do, and approve it.

**4. Open your specification.** Claude tells you where it saved it, usually
`docs/<your product's name>/specs/` in this folder. Ask:

> Open the specification in my browser.

Or do it yourself: double-click `index.cmd` in that folder on Windows. On macOS, run
`index.sh` the same way as in step 4.

## Step 7: Change it

The website is for reading. To change anything, ask Claude in the terminal:

> Use specs-builder-2. In R4, the limit should be six, not five.

Claude shows you everything the change affects, the other requirements and the
screens, and waits for your yes before it changes anything.

Anyone reading the website can press **Request a change** on any page or card. The
request waits under **What is open**. To deal with it, tell Claude:

> Use specs-builder-2. Take the requests in the inbox.

## Step 8: Share it

Press **Export** at the top of the website. You get one HTML file that holds the
whole specification. Anyone can open it in a browser, with nothing to install.

To keep working on it elsewhere, copy its whole folder. Your specification is plain
text files that belong to you.

## If something goes wrong

| What you see | What to do |
|---|---|
| `python` is not recognized, or the Microsoft Store opens | Python isn't set up. Install it again and tick **Add python.exe to PATH**, then open a new terminal |
| `specs-builder-2 needs Python 3.14 or later` | You have an older Python. Install 3.14 or later |
| `claude` is not recognized, or `command not found` | Close the terminal and open a new one. If it still fails, see [Claude Code's install help](https://code.claude.com/docs/en/troubleshoot-install.md) |
| Windows won't run a `.cmd` file | Choose **More info**, then **Run anyway** |
| The Graph page or flow diagrams don't appear | They need an internet connection |
| Claude doesn't seem to use the tool | Check you started `claude` in this folder, and say `specs-builder-2` in your request |
| The website looks out of date | Close the black window and open it again |

To check Claude Code itself, run `claude doctor` in a terminal.

## Where to go next

- [The tutorial](.claude/skills/specs-builder-2/TUTORIAL.html) walks you through
  reading, writing, changing and finishing a specification, with pictures.
- [The user manual](.claude/skills/specs-builder-2/USER-MANUAL.html) explains
  everything the tool does.
- [What it cannot do yet](.claude/skills/specs-builder-2/USER-MANUAL.md#what-it-cannot-do-yet)
  lists its limits.
- `.claude/skills/specs-builder-2/examples/` holds six finished specifications. Each
  has an `index.cmd` and an `index.sh` in its `specs` folder.
- `targets/novalife-2/` is a real project, the NovaLife Clinic website. Run
  **open-novalife.cmd**, or `sh open-novalife.sh`, to see a specification written
  for an actual product. To work on it, name it: "Use specs-builder-2 on
  `targets/novalife-2/specs`."
