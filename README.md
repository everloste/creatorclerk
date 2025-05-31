# Creator Clerk
Clerk is a utility for downloading CurseForge and Modrinth creator stats
into your local SQLite database.

As of right now, Clerk only collects data and can export it.
Only Windows is supported, although I'd like Linux eventually as well
so you can have Clerk on a lightweight server.

## Usage
The program is currently GUI-less since right now it only does data collection.
You can use the program from your terminal with system arguments.

A log file will be created on first launch where you'll find
the result of every command ran.
You can also use the `-wait` flag to signal to the program you don't want the
console to immediately close, but only after user input.

---
Start the command prompt or PowerShell,
then with `clerk` referring to the location of the executable,
whether you `cd` or not:

To add a new account:
```
clerk add curseforge "My CurseForge account"
```
Use `curseforge` or `cf` for CurseForge and `modrinth` for Modrinth.

Then, to add a cookie file to the account:
```
clerk cookies add "My CurseForge account" "C:/cookie_file.json"
```

You are providing a path to a cookie file on disk,
which will be accessed every time the program collects data.
If need be, delete the file and the program will no longer
be able to access your page.
Anyone with access to the cookie file will be able to access your
data.
You can remove the link to the cookie file with `cookies remove "My CurseForge Account"`.

You can get the cookies for your session with a browser extension,
specifically [cookie-editor](https://cookie-editor.com/). **⚠ Currently only the JSON format is supported.**

To make sure everything's working, you can try to get your current balance online:
```
clerk connect "My CurseForge Account"
```

This will connect to the relevant URL and print out your balance in USD in the console.

Then finally, to get the current balance in all accounts and add that to the database:
```
clerk collect
```

To export the data to a CSV file:
```
clerk export "C:/Users/Bee/Downloads"
```

## Automating Clerk
On Windows, you can automate Clerk by creating a scheduled task in Task Scheduler.
Make sure the arguments include the `collect` command!
