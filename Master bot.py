from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import json
import os

TOKEN = "8374862176:AAFe_ph7XmTsfBOg-sw5PZm1x6kZStZq4uA"
DATA_FILE = "builder_data.json"

# ====== HARDCODED MASTER ADMIN ======
MASTER_ADMIN_ID = 123456789  # ← REPLACE with your Telegram user ID

if os.path.exists(DATA_FILE):
    with open(DATA_FILE) as f:
        data = json.load(f)
else:
    data = {"bots": {}, "requests": []}

bots = data["bots"]
requests = data["requests"]

def save():
    with open(DATA_FILE, "w") as f:
        json.dump({"bots": bots, "requests": requests}, f)

BOT_CODE = '''
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import json, os

TOKEN = "{token}"
ADMINS = {admins}
BOT_NAME = "{bot_name}"
WELCOME = """{welcome}"""
SMART = {smart}
MULTI = {multi}
DATA = "{bot_name}.json"

def load():
    if os.path.exists(DATA):
        with open(DATA) as f: return json.load(f)
    return {{"files":{{}}}}
def save(files):
    with open(DATA,"w") as f: json.dump({{"files":files}},f)

filedb = load().get("files",{{}})
wait = None

async def h(update, context):
    global filedb, wait
    m = update.message
    uid = m.from_user.id
    t = m.text.strip() if m.text else ""

    if m.document:
        if uid in ADMINS and wait:
            kw = wait
            if kw not in filedb: filedb[kw]=[]
            if not MULTI: filedb[kw]=[]
            filedb[kw].append(m.document.file_id)
            wait = None
            save(filedb)
            await m.reply_text(f"Saved: {{kw}}")
        return

    if t=="/start":
        await m.reply_text(WELCOME)
        return
    if t=="/list":
        if filedb:
            r = "\\n".join(f"• {{k}} ({{len(v)}})" for k,v in filedb.items())
            await m.reply_text(f"Keywords:\\n{{r}}")
        else: await m.reply_text("No files.")
        return
    if t.startswith("/add") and uid in ADMINS:
        p=t.split(" ",1)
        if len(p)>1:
            wait = p[1].lower()
            await m.reply_text(f"Send file for: {{p[1]}}")
        return
    if t.startswith("/del") and uid in ADMINS:
        p=t.split(" ",1)
        if len(p)>1 and p[1].lower() in filedb:
            del filedb[p[1].lower()]
            save(filedb)
            await m.reply_text(f"Deleted: {{p[1]}}")
        return
    if t=="/help":
        await m.reply_text("Type keyword to search files.\\n/list - browse all")
        return

    kw = t.lower()
    if kw in filedb:
        for fid in filedb[kw]: await m.reply_document(fid)
        return
    if SMART:
        for sk in filedb:
            if sk in kw:
                for fid in filedb[sk]: await m.reply_document(fid)
                return
    await m.reply_text(f"No file: {{t}}")

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, h))
print(f"{{BOT_NAME}} running!")
app.run_polling()
'''

USER_GUIDE = """
📖 *Complete Guide to Create Your Own Bot*

━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 *STEP 1: Request a Bot*
Send: `/request YourBotName`
Example: `/request MathNotes`
⏳ Wait for admin approval.

━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 *STEP 2: Admin Approves*
You'll get a message when approved.

━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 *STEP 3: Create Bot on Telegram*
1️⃣ Search *@BotFather*
2️⃣ Send `/newbot`
3️⃣ Send a name: `Math Notes`
4️⃣ Send username: `mathnotes123_bot`
5️⃣ Copy the token

━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 *STEP 4: Submit Token*
Send: `/mytoken BotName TOKEN`

━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 *STEP 5: Get Your Bot File*
Download the `.py` file.

━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 *STEP 6: Run Your Bot*
📱 Android: Pydroid 3 → Open file → ▶️ Run
☁️ 24/7: pythonanywhere.com → Upload → Run

━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 *STEP 7: Use Your Bot*
Admin: /add keyword → send file
Users: Type keyword → get file

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ Help: @manikantahere
"""

ADMIN_GUIDE = """
👑 *Admin Guide*

📩 /requests — View pending requests
✅ /approve ID — Approve
❌ /deny ID — Deny
⚡ /create name — Quick create
🔑 /settoken name TOKEN
📦 /generate name — Get code
📋 /listbots — All bots
🔍 /smart name — Toggle search
📚 /multi name — Toggle multi-file
🗑️ /delbot name — Delete bot
"""

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bots, requests
    m = update.message
    uid = m.from_user.id
    t = m.text.strip() if m.text else ""

    is_admin = (uid == MASTER_ADMIN_ID)

    if t == "/start":
        if is_admin:
            await m.reply_text(ADMIN_GUIDE, parse_mode="Markdown")
        else:
            await m.reply_text("🤖 *Welcome to Bot Builder!*\n\nCreate your own Telegram file-search bot — no coding!\n\n📖 /guide — Full tutorial\n📩 /request name — Request bot\n📋 /mystatus — Your requests", parse_mode="Markdown")
        return

    if t == "/help":
        if is_admin:
            await m.reply_text(ADMIN_GUIDE, parse_mode="Markdown")
        else:
            await m.reply_text(USER_GUIDE, parse_mode="Markdown")
        return

    if t == "/guide":
        await m.reply_text(USER_GUIDE, parse_mode="Markdown")
        return

    # /request — Anyone
    if t.startswith("/request"):
        p = t.split(" ", 1)
        if len(p) < 2:
            await m.reply_text("⚠️ /request BotName\nExample: /request MathNotes")
            return
        name = p[1].strip()
        for r in requests:
            if r["name"] == name and r["status"] == "pending":
                await m.reply_text("⚠️ Already pending. Check /mystatus")
                return
        req = {"id": len(requests)+1, "user": uid, "name": name, "status": "pending"}
        requests.append(req)
        save()
        await m.reply_text(f"📩 Request #{req['id']}: *{name}*\nStatus: Pending\n\nCheck: /mystatus", parse_mode="Markdown")
        await context.bot.send_message(MASTER_ADMIN_ID, f"📩 New request #{req['id']}\nFrom: {uid}\nBot: {name}\n\n/approve {req['id']} | /deny {req['id']}")
        return

    # /mystatus — Anyone
    if t == "/mystatus":
        my = [r for r in requests if r["user"] == uid]
        if not my:
            await m.reply_text("📭 No requests.\nSend /request BotName")
        else:
            s = "📋 *Your Requests*\n\n"
            for r in my:
                e = "⏳" if r["status"]=="pending" else "✅" if r["status"]=="approved" else "❌"
                s += f"{e} #{r['id']} {r['name']} - {r['status']}\n"
            appr = [r for r in my if r["status"]=="approved"]
            if appr:
                s += "\n✅ *Submit your token:*\n"
                for r in appr:
                    s += f"`/mytoken {r['name']} TOKEN`\n"
            await m.reply_text(s, parse_mode="Markdown")
        return

    # /mytoken — Anyone
    if t.startswith("/mytoken"):
        p = t.split(" ", 2)
        if len(p) < 3:
            await m.reply_text("⚠️ /mytoken BotName TOKEN\n\nGet token from @BotFather after /newbot")
            return
        name, tok = p[1], p[2]
        if name in bots and uid in bots[name]["admins"]:
            bots[name]["token"] = tok
            save()
            b = bots[name]
            code = BOT_CODE.format(token=b["token"], admins=b["admins"], bot_name=name, welcome=b["welcome"], smart=b["smart"], multi=b["multi"])
            fname = f"{name}.py"
            with open(fname,"w") as f: f.write(code)
            await m.reply_document(open(fname,"rb"), filename=fname)
            await m.reply_text(f"🎉 *{name} is ready!*\n\n📥 Download the file\n📱 Run on Pydroid 3\n\nYour commands:\n/add keyword — Add file\n/del keyword — Remove\n/list — View all", parse_mode="Markdown")
        else:
            await m.reply_text("❌ Not authorized. Get approval first: /request BotName")
        return

    # === ADMIN ONLY BELOW ===
    if not is_admin:
        await m.reply_text("🤖 Use /request to create your bot.\n📖 /guide for tutorial")
        return

    if t == "/requests":
        pending = [r for r in requests if r["status"]=="pending"]
        if not requests:
            await m.reply_text("No requests yet.")
        else:
            s = "📋 *Requests*\n\n"
            for r in requests[-20:]:
                e = "⏳" if r["status"]=="pending" else "✅" if r["status"]=="approved" else "❌"
                s += f"{e} #{r['id']} {r['name']} by {r['user']}\n"
            if pending:
                s += f"\n⚡ {len(pending)} pending"
            await m.reply_text(s, parse_mode="Markdown")
        return

    if t.startswith("/approve"):
        p = t.split(" ",1)
        if len(p)<2: return
        try: rid=int(p[1])
        except: return
        for r in requests:
            if r["id"]==rid and r["status"]=="pending":
                r["status"]="approved"
                name=r["name"]
                bots[name]={"token":"","admins":[r["user"]],"welcome":f"🎓 Welcome to {name}!\n\nType keyword to get files.\n/list - browse all","smart":True,"multi":True}
                save()
                await context.bot.send_message(r["user"],f"🎉 *Approved! {name}*\n\n1️⃣ Go to @BotFather\n2️⃣ /newbot → create bot\n3️⃣ Copy token\n4️⃣ Send here:\n`/mytoken {name} TOKEN`\n\n/guide for help",parse_mode="Markdown")
                await m.reply_text(f"✅ Approved #{rid}")
                return
        return

    if t.startswith("/deny"):
        p=t.split(" ",1)
        if len(p)<2: return
        try: rid=int(p[1])
        except: return
        for r in requests:
            if r["id"]==rid and r["status"]=="pending":
                r["status"]="denied"
                save()
                await context.bot.send_message(r["user"],f"❌ Request denied: {r['name']}")
                await m.reply_text(f"❌ Denied #{rid}")
                return
        return

    if t.startswith("/create"):
        p=t.split(" ",1)
        if len(p)<2: return
        name=p[1].strip()
        if name in bots:
            await m.reply_text("Exists.")
            return
        bots[name]={"token":"","admins":[uid],"welcome":f"🎓 Welcome to {name}!","smart":True,"multi":True}
        save()
        await m.reply_text(f"✅ Created {name}\n/settoken {name} TOKEN")
        return

    if t.startswith("/settoken"):
        p=t.split(" ",2)
        if len(p)<3: return
        name,tok=p[1],p[2]
        if name in bots:
            bots[name]["token"]=tok
            save()
            await m.reply_text(f"✅ /generate {name}")
        return

    if t.startswith("/generate"):
        p=t.split(" ",1)
        if len(p)<2: return
        name=p[1]
        if name not in bots or not bots[name].get("token"):
            await m.reply_text("Not ready.")
            return
        b=bots[name]
        code=BOT_CODE.format(token=b["token"],admins=b["admins"],bot_name=name,welcome=b["welcome"],smart=b["smart"],multi=b["multi"])
        fname=f"{name}.py"
        with open(fname,"w") as f: f.write(code)
        await m.reply_document(open(fname,"rb"),filename=fname)
        return

    if t=="/listbots":
        if not bots:
            await m.reply_text("No bots.")
        else:
            s="🤖 Bots:\n\n"
            for n,c in bots.items():
                s+=f"• {n} | Token: {'✅' if c.get('token') else '❌'}\n"
            await m.reply_text(s)
        return

    if t.startswith("/smart"):
        p=t.split(" ",1)
        if len(p)>1 and p[1] in bots:
            bots[p[1]]["smart"]=not bots[p[1]].get("smart",True)
            save()
            await m.reply_text(f"Smart: {'ON' if bots[p[1]]['smart'] else 'OFF'}")
        return

    if t.startswith("/multi"):
        p=t.split(" ",1)
        if len(p)>1 and p[1] in bots:
            bots[p[1]]["multi"]=not bots[p[1]].get("multi",True)
            save()
            await m.reply_text(f"Multi: {'ON' if bots[p[1]]['multi'] else 'OFF'}")
        return

    if t.startswith("/delbot"):
        p=t.split(" ",1)
        if len(p)>1 and p[1] in bots:
            del bots[p[1]]
            save()
            await m.reply_text(f"Deleted {p[1]}")
        return

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle))
    print("🤖 Master Builder running!")
    app.run_polling()

main()
