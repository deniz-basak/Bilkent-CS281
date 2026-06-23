import FreeSimpleGUI as sg
import sqlite3
import datetime
import uuid
import os

sg.theme("DarkPurple6")
con = sqlite3.connect('Project.db')
cur = con.cursor()

def login():
    layout = [
        [sg.Text("Choose login option: ")],
        [sg.Button("User", size=(20,1)), sg.Button("Admin", size=(20,1))],
        [sg.Button("Quit", size=(10,1))],
    ]
    window = sg.Window("Login Page", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Quit":
            break
        elif event == "User":
            window.close()
            user_login()
        elif event == "Admin":
            window.close()
            admin_login()
    window.close()

def user_login():
    username = []
    usernameList = []
    pw = []
    pwList = []
    infoTable = []
    info = []
    for table in cur.execute("""SELECT NUsername FROM UserAccount ORDER BY NUsername"""):
        username.append(table)
    for name in username:
        usernameList.append(name[0])

    for ptable in cur.execute("""SELECT Password FROM User ORDER BY Username"""):
        pw.append(ptable)
    for password in pw:
        pwList.append(password[0])

    for table in cur.execute("""SELECT Username, Password FROM User"""):
        infoTable.append(table)
    for row in infoTable:
        info.append((row[0], row[1]))

    layout = [
        [sg.Text("Username:"), sg.Input(key="Username")],
        [sg.Text("Password:"), sg.Input(key="Password", password_char="*")],
        [[sg.Text(key="out")]],
        [sg.Button("Back"), sg.Button("Login")],
    ]
    window = sg.Window("User Login", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            login()
        elif event == "Login":
            if values["Username"] in usernameList:
                if values["Password"] in pwList:
                    if (values["Username"], values["Password"]) in info:
                        window.close()
                        user_page(values["Username"])
                    else:
                        window["out"].update("Wrong password, please try again")
                elif values["Password"] not in pwList:
                    window["out"].update("Wrong password, please try again")
            elif values["Username"] not in usernameList:
                window["out"].update("User not found")
    window.close()

def admin_login():
    username = []
    usernameList = []
    pw = []
    pwList = []
    infoTable = []
    info = []
    for table in cur.execute("""SELECT AUsername FROM AdminAccount ORDER BY AUsername"""):
        username.append(table)
    for name in username:
        usernameList.append(name[0])

    for ptable in cur.execute("""SELECT Password FROM User ORDER BY Username"""):
        pw.append(ptable)
    for password in pw:
        pwList.append(password[0])

    for table in cur.execute("""SELECT Username, Password FROM User"""):
        infoTable.append(table)
    for row in infoTable:
        info.append((row[0], row[1]))

    layout = [
        [sg.Text("Username:"), sg.Input(key="Username")],
        [sg.Text("Password:"), sg.Input(key="Password", password_char="*")],
        [sg.Text(key="out")],
        [sg.Button("Back"), sg.Button("Login")]
    ]

    window = sg.Window("Admin Login", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            login()
            return
        elif event == "Login":
            if values["Username"] in usernameList:
                if values["Password"] in pwList:
                    if (values["Username"], values["Password"]) in info:
                        window.close()
                        admin_posts()
                    else:
                        window["out"].update("Wrong password, please try again")
                elif values["Password"] not in pwList:
                    window["out"].update("Wrong password, please try again")
            elif values["Username"] not in usernameList:
                window["out"].update("Admin not found")
    window.close()

def admin_posts():
    posts = []
    post_ids = []

    layout = [
        [
            sg.Text("Creator"), sg.Input(key="CREATOR", size=15),
            sg.Text("After Date"), sg.Input(key="DATE", size=12),
            sg.Button("Apply Filter"), sg.Button("Clear")
        ],
        [sg.Table(
            headings=["Creator", "Description", "Date"],
            values=[],
            key="POSTS",
            auto_size_columns=False,
            col_widths=[15, 40, 12],
            justification="left",
            num_rows=12
        )],
        [sg.Button("View"), sg.Button("Logout")]
    ]

    window = sg.Window("Manage Posts", layout, finalize=True)

    def load(creator="", date=""):
        posts.clear()
        post_ids.clear()

        query = """
        SELECT P.PostID, UCC.NUsername, P.PostDescription, P.ReleaseDate
        FROM Post P
        JOIN UserCreatesContent UCC ON P.PostID = UCC.ContentID
        WHERE 1=1
        """
        params = []

        if creator:
            query += " AND UCC.NUsername LIKE ?"
            params.append("%" + creator + "%")

        if date:
            query += " AND P.ReleaseDate >= ?"
            params.append(date)

        query += " ORDER BY P.ReleaseDate DESC"

        for row in cur.execute(query, params):
            post_ids.append(row[0])
            posts.append([row[1], row[2], row[3]])

        window["POSTS"].update(posts)

    load()

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Logout":
            window.close()
            login()
            return
        elif event == "Apply Filter":
            load(values["CREATOR"], values["DATE"])
        elif event == "Clear":
            window["CREATOR"].update("")
            window["DATE"].update("")
            load()
        elif event == "View" and values["POSTS"]:
            idx = values["POSTS"][0]
            post_id = post_ids[idx]
            window.close()
            admin_post_detail(post_id)
            return
    window.close()

def admin_post_detail(post_id):
    desc, date, creator = "", "", ""
    likes = 0
    comments = []

    cur.execute("""
        SELECT P.PostDescription, P.ReleaseDate, UCC.NUsername
        FROM Post P
        JOIN UserCreatesContent UCC ON P.PostID = UCC.ContentID
        WHERE P.PostID = ?
    """, (post_id,))
    desc, date, creator = cur.fetchone()

    likes = cur.execute(
        "SELECT COUNT(*) FROM Likes WHERE ContentID = ?", (post_id,)
    ).fetchone()[0]

    for row in cur.execute("""
        SELECT WriterUN, TextContent
        FROM Comment
        WHERE ComContentID = ?
        ORDER BY ComDate
    """, (post_id,)):
        comments.append([row[0], row[1]])

    layout = [
        [sg.Text("Post Review")],
        [sg.Text("Creator:", size=(10,1)), sg.Text(creator)],
        [sg.Text("Date:", size=(10,1)), sg.Text(str(date))],
        [sg.Text("Likes:", size=(10,1)), sg.Text(str(likes))],
        [sg.Text("Description:", size=(10,1)), sg.Text(desc)],
        [sg.Text("Comments:")],
        [sg.Table(
            values=comments,
            headings=["User", "Comment"],
            auto_size_columns=False,
            col_widths=[15, 40],
            num_rows=8
        )],
        [sg.Button("Delete Post"), sg.Button("Back")]
    ]

    window = sg.Window("Post Review", layout)

    while True:
        event, _ = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            admin_posts()
            return
        elif event == "Delete Post":
            cur.execute("DELETE FROM Likes WHERE ContentID=?", (post_id,))
            cur.execute("DELETE FROM Comment WHERE ComContentID=?", (post_id,))
            cur.execute("DELETE FROM Tag WHERE TagMediaID IN (SELECT MediaID FROM Media WHERE PostID=?)", (post_id,))
            cur.execute("DELETE FROM Photo WHERE PhotoID IN (SELECT MediaID FROM Media WHERE PostID=?)", (post_id,))
            cur.execute("DELETE FROM Video WHERE VideoID IN (SELECT MediaID FROM Media WHERE PostID=?)", (post_id,))
            cur.execute("DELETE FROM Media WHERE PostID=?", (post_id,))
            cur.execute("DELETE FROM UserCreatesContent WHERE ContentID=?", (post_id,))
            cur.execute("DELETE FROM Post WHERE PostID=?", (post_id,))
            con.commit()
            sg.popup("Post deleted")
            window.close()
            admin_posts()
            return
    window.close()

def user_page(username):
    name = cur.execute("SELECT Name FROM User WHERE Username = ?", (username,)).fetchone()[0]
    layout = [
        [sg.Text("Welcome " + name)],
        [sg.Button("Homepage", size=(10,1)), sg.Button("Connections", size=(10,1))],
        [sg.Button("Create Post", size=(10,1)), sg.Button("Create Story", size=(10,1))],
        [sg.Button("Edit Profile", size=(10,1)), sg.Button("Interactions", size=(10,1))],
        [sg.Button("Story Archive", size=(10,1)), sg.Button("My Posts", size=(10,1))],
        [sg.Button("Logout", size=(10,1))]
    ]

    window = sg.Window("User Page", layout)

    while True:
        event, _ = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Logout":
            window.close()
            login()
            return
        elif event == "Homepage":
            window.close()
            home_page(username)
            return
        elif event == "Interactions":
            window.close()
            interactions_page(username)
            return
        elif event == "Connections":
            window.close()
            connections_page(username)
            return
        elif event == "Edit Profile":
            window.close()
            complete_profile(username)
            user_page(username)
            return
        elif event == "Create Post":
            window.close()
            create_post(username)
            return
        elif event == "Create Story":
            window.close()
            create_story(username)
            return
        elif event == "Story Archive":
            window.close()
            story_archive_page(username)
            return
        elif event == "My Posts":
            window.close()
            my_posts(username)
            return
    window.close()

def story_archive_page(username):
    stories = []
    story_ids = []

    for s in cur.execute("""
        SELECT S.StoryID, S.Content, S.UpTime
        FROM UserCreatesContent UCC
        JOIN Story S ON UCC.ContentID = S.StoryID
        WHERE UCC.NUsername = ?
        AND datetime(S.UpTime, '+1 day') <= datetime('now')
        ORDER BY S.UpTime DESC
    """, (username,)):
        story_ids.append(s[0])
        stories.append([s[1], s[2]])

    layout = [
        [sg.Text("Your Story Archive")],
        [sg.Table(stories, ["Content", "Date"], key="ARCHIVE",
                  auto_size_columns=True, num_rows=8,
                  enable_events=True)],
        [sg.Button("View"), sg.Button("Back")]
    ]

    window = sg.Window("Story Archive", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            user_page(username)
            return
        elif event == "View" and values["ARCHIVE"]:
            idx = values["ARCHIVE"][0]
            sid = story_ids[idx]
            window.close()
            story_detail_page(sid, username)
            return
    window.close()


def create_story(username):
    layout = [
        [sg.Text("Story Content")],
        [sg.Input(key="TEXT", size=50)],
        [sg.Button("Create Story"), sg.Button("Back")]
    ]

    window = sg.Window("Create Story", layout, finalize=True)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            user_page(username)
            return
        elif event == "Create Story":
            if not values["TEXT"]:
                sg.popup("Please enter story content")
                continue           
            cur.execute("SELECT MAX(ContentID) FROM UserCreatesContent")
            content_id = (cur.fetchone()[0]) + 1

            link = f"https://contents.com/mystory{content_id}"

            cur.execute("INSERT INTO UserCreatesContent VALUES (?, ?, ?)",
                        (content_id, link, username))

            cur.execute("""
                INSERT INTO Story VALUES (?, ?, datetime('now'))
            """, (content_id,values["TEXT"]))

            con.commit()
            sg.popup("Story created")
            window.close()
            user_page(username)
            return
    window.close()


def create_post(username):
    cur.execute("""
        SELECT FollowingUN 
        FROM Follow
        WHERE FollowerUN = ?
    """, (username,))
    followed = [x[0] for x in cur.fetchall()]

    layout = [
        [sg.Text("Post Description")],
        [sg.Input(key="DESC", size=50)],
        [sg.FileBrowse("Select Media File", key="MEDIAFILE"), sg.Button("Tag Users"), sg.Button("Confirm Upload", key="UPLOAD")],
        [sg.Text("Added Media")],
        [sg.Listbox(values=[], size=(50, 5), key="TAGGEDUSERS")],
        [sg.Button("Create Post"), sg.Button("Back")]
    ]

    window = sg.Window("Create Post", layout, finalize=True)

    current_tags = []
    media_list = []

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            user_page(username)
            return
        elif event == "Tag Users":
            tag_layout = [
                [sg.Text("Select users to tag")],
                [sg.Listbox(followed, select_mode=sg.SELECT_MODE_MULTIPLE, size=(30,8), key="TAGS")],
                [sg.Button("OK")]
            ]

            tag_win = sg.Window("Tag Users", tag_layout, modal=True)

            ev, vals = tag_win.read()
            if ev == "OK":
                current_tags = vals["TAGS"]
            tag_win.close()
            continue

        elif event == "UPLOAD":
            media_file = values["MEDIAFILE"]
            if not media_file:
                sg.popup("No media chosen")
                continue

            if any(media_file == n[0] for n in media_list):
                sg.popup("This media file has already been uploaded")
                window["MEDIAFILE"].update("Select Media File")
                current_tags = []
                continue

            media_list.append((media_file, current_tags.copy()))
            tag_display_list = [
                f"{i+1}. {os.path.basename(mfile)} - {', '.join(tags) if tags else '-- No tags --'}"
                for i, (mfile, tags) in enumerate(media_list)
            ]
            window["TAGGEDUSERS"].update(tag_display_list)
            window["MEDIAFILE"].update("Select Media File")
            current_tags = []

        elif event == "Create Post":
            if not values["DESC"]:
                sg.popup("Description cannot be empty")
                continue
            elif not media_list:
                sg.popup("No media uploaded")
                continue

            post_id = str(uuid.uuid4().fields[-1])[:5]


            link = f"https://contents.com/mypost{post_id}"
            today = datetime.date.today().isoformat()

            cur.execute("INSERT INTO UserCreatesContent VALUES (?, ?, ?)",
                        (post_id, link, username))
            cur.execute("INSERT INTO Post VALUES (?, ?, ?)",
                        (post_id, values["DESC"], today))

            for i, (mlink, tags) in enumerate(media_list):
                cur.execute("INSERT INTO Media (Resolution, PostID) VALUES (?, ?)", ("1080p", post_id))
                mid = max(cur.execute("SELECT MediaID FROM Media").fetchall())[0]

                if mlink.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    cur.execute("INSERT INTO Photo VALUES (?)", (mid,))
                else:
                    cur.execute("INSERT INTO Video VALUES (?, ?)", (mid, 60))

                for t in tags:
                    cur.execute("INSERT INTO Tag VALUES (?, ?)", (t, mid))
            con.commit()
            sg.popup("Post Created")
            window.close()
            user_page(username)
            return
    window.close()

def complete_profile(username):
    cur.execute("""
        SELECT AccDescription, Information, AccountPrivacy
        FROM UserAccount
        WHERE NUsername = ?
    """, (username,))
    row = cur.fetchone()

    desc = row[0] if row else ""
    info = row[1] if row else ""
    private = bool(row[2]) if row else False

    layout = [
        [sg.Text("Complete Profile")],
        [sg.Text("Profile Description")],
        [sg.Input(desc, key="DESC")],
        [sg.Text("Personal Information")],
        [sg.Input(info, key="INFO")],
        [sg.Checkbox("Private Account", default=private, key="PRIVATE")],
        [sg.Button("Save"), sg.Button("Back")]
    ]

    window = sg.Window("Profile Settings", layout, finalize=True)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            user_page(username)
            return
        elif event == "Save":
            privacy = 1 if values["PRIVATE"] else 0
            cur.execute("""
                UPDATE UserAccount
                SET AccDescription = ?, Information = ?, AccountPrivacy = ?
                WHERE NUsername = ?
            """, (values["DESC"], values["INFO"], privacy, username))
            con.commit()
            sg.popup("Profile updated")
    window.close()

def my_posts(username):
    post_ids = []
    post_rows = []

    story_ids = []
    story_rows = []

    for p in cur.execute("""
        SELECT P.PostID, P.PostDescription, P.ReleaseDate
        FROM Post P
        JOIN UserCreatesContent UCC ON P.PostID = UCC.ContentID
        WHERE UCC.NUsername = ?
        ORDER BY P.ReleaseDate DESC
    """, (username,)):
        post_ids.append(p[0])
        post_rows.append([username, p[1], p[2]])

    for s in cur.execute("""
        SELECT S.StoryID, S.Content, S.UpTime
        FROM Story S
        JOIN UserCreatesContent UCC ON S.StoryID = UCC.ContentID
        WHERE UCC.NUsername = ?
        AND datetime(S.UpTime, '+1 day') > datetime('now')
        ORDER BY S.UpTime DESC
    """, (username,)):
        story_ids.append(s[0])
        story_rows.append([username, s[1], s[2]])

    layout = [
        [sg.Text("My Stories")],
        [sg.Table(
            values=story_rows,
            headings=["Owner", "Story Content", "Date"],
            col_widths=[15, 30, 18],
            auto_size_columns=False,
            justification="left",
            num_rows=5,
            key="STORIES",
            enable_events=True
        )],
        [sg.Button("View Story"), sg.Button("Story Archive")],
        [sg.HorizontalSeparator()],
        [sg.Text("My Posts")],
        [sg.Table(
            values=post_rows,
            headings=["Owner", "Description", "Date"],
            col_widths=[15, 30, 18],
            auto_size_columns=False,
            justification="left",
            num_rows=10,
            key="POSTS",
            enable_events=True
        )],
        [sg.Button("View Post"), sg.Button("Back")]
    ]

    window = sg.Window("My Profile", layout, finalize=True)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            user_page(username)
            return
        elif event == "View Post" and values["POSTS"]:
            idx = values["POSTS"][0]
            window.close()
            post_detail_page(post_ids[idx], username)
            return
        elif event == "View Story" and values["STORIES"]:
            idx = values["STORIES"][0]
            window.close()
            story_detail_page(story_ids[idx], username)
            return
        elif event == "Story Archive":
            window.close()
            story_archive_page(username)
            return
    window.close()

def interactions_page(username):
    layout = [
        [sg.Text("Interactions")],
        [sg.Button("Liked Posts"), sg.Button("Your Comments")],
        [sg.Button("Back")]
    ]

    window = sg.Window("Interactions", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            user_page(username)
            return
        elif event == "Liked Posts":
            window.close()
            liked_posts(username)
            return
        elif event == "Your Comments":
            window.close()
            user_comments(username)
            return
    window.close()

def liked_posts(username):
    rows = []
    post_ids = []

    for row in cur.execute("""
        SELECT P.PostID, UCC.NUsername, P.PostDescription, P.ReleaseDate
        FROM Likes L
        JOIN Post P ON L.ContentID = P.PostID
        JOIN UserCreatesContent UCC ON P.PostID = UCC.ContentID
        WHERE L.NUsername = ?
        ORDER BY P.ReleaseDate DESC
    """, (username,)):
        post_ids.append(row[0])
        rows.append([row[1], row[2], row[3]])

    layout = [
        [sg.Text("Posts You Liked")],
        [sg.Table(rows, ["Owner", "Description", "Date"], 
                  col_widths=[15, 30, 18], key="TABLE", 
                  enable_events=True)],
        [sg.Button("View"), sg.Button("Back")]
    ]

    window = sg.Window("Liked Posts", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            interactions_page(username)
            return
        elif event == "View" and values["TABLE"]:
            idx = values["TABLE"][0]
            window.close()
            post_detail_page(post_ids[idx], username)
            return
    window.close()

def user_comments(username):
    rows = []

    for row in cur.execute("""
        SELECT UCC.NUsername, P.PostDescription, C.TextContent, C.ComDate
        FROM Comment C
        JOIN Post P ON C.ComContentID = P.PostID
        JOIN UserCreatesContent UCC ON P.PostID = UCC.ContentID
        WHERE C.WriterUN = ?
        ORDER BY C.ComDate DESC
    """, (username,)):
        rows.append([row[0], row[1], row[2], row[3]])

    layout = [
        [sg.Text("Your Comments")],
        [sg.Table(rows, ["Post Owner", "Post", "Your Comment", "Date"], col_widths=[15, 25, 25, 15])],
        [sg.Button("Back")]
    ]

    window = sg.Window("Your Comments", layout)

    while True:
        event, _ = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            interactions_page(username)
            return
    window.close()

def connections_page(username):
    followersc = cur.execute("SELECT COUNT(*) FROM Follow WHERE FollowingUN = ?", (username,)).fetchone()[0]
    followingc = cur.execute("SELECT COUNT(*) FROM Follow WHERE FollowerUN = ?", (username,)).fetchone()[0]

    followers = []
    following = []
    discover = []

    for f in cur.execute("SELECT FollowerUN FROM Follow WHERE FollowingUN = ?", (username,)):
        followers.append([f[0]])

    for f in cur.execute("SELECT FollowingUN FROM Follow WHERE FollowerUN = ?", (username,)):
        following.append([f[0]])

    for u in cur.execute("""
        SELECT NUsername FROM UserAccount
        WHERE NUsername != ?
        AND NUsername NOT IN (SELECT FollowingUN FROM Follow WHERE FollowerUN = ?)
    """, (username, username)):
        discover.append([u[0]])

    layout = [
        [sg.Text(f"Followers: {followersc}   Following: {followingc}")],
        [
            sg.Table(followers, ["Followers"], size=(15,8), key="FOLLOWERS"),
            sg.Table(following, ["Following"], size=(15,8), key="FOLLOWING"),
            sg.Table(discover, ["Find People"], size=(15,8), key="DISCOVER")
        ],
        [sg.Button("Follow"), sg.Button("Unfollow"), sg.Button("View Profile")],
        [sg.Button("Back")]
    ]

    window = sg.Window("Connections", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            user_page(username)
            return
        elif event == "Follow" and values["DISCOVER"]:
            target = discover[values["DISCOVER"][0]][0]
            cur.execute("INSERT INTO Follow VALUES (?, ?)", (username, target))
            con.commit()
            window.close()
            connections_page(username)
            return
        elif event == "Unfollow" and values["FOLLOWING"]:
            target = following[values["FOLLOWING"][0]][0]
            cur.execute("""
                DELETE FROM Follow
                WHERE FollowerUN=? AND FollowingUN=?
            """, (username, target))
            con.commit()
            window.close()
            connections_page(username)
            return
        elif event == "View Profile":
            target = None
            if values["FOLLOWERS"]:
                target = followers[values["FOLLOWERS"][0]][0]
            elif values["FOLLOWING"]:
                target = following[values["FOLLOWING"][0]][0]
            elif values["DISCOVER"]:
                target = discover[values["DISCOVER"][0]][0]
            if target:
                window.close()
                view_user_profile(target, username)
    window.close()    

def view_user_profile(target, viewer):
    cur.execute("""
        SELECT U.Name, UA.AccDescription, UA.Information, UA.AccountPrivacy
        FROM User U
        JOIN UserAccount UA ON U.Username = UA.NUsername
        WHERE U.Username = ?
    """, (target,))
    row = cur.fetchone()

    if not row:
        sg.popup("User not found")
        return

    name, adesc, info, private = row

    cur.execute("SELECT COUNT(*) FROM Follow WHERE FollowingUN=?", (target,))
    followers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM Follow WHERE FollowerUN=?", (target,))
    following = cur.fetchone()[0]

    cur.execute("""
        SELECT 1 FROM Follow 
        WHERE FollowerUN=? AND FollowingUN=?
    """, (viewer, target))
    is_following = cur.fetchone() is not None

    can_view_content = (not private) or is_following or (viewer == target)

    posts = []
    post_ids = []

    stories = []
    story_ids = []

    if can_view_content:
        for p in cur.execute("""
            SELECT P.PostID, P.PostDescription, P.ReleaseDate
            FROM UserCreatesContent UCC
            JOIN Post P ON UCC.ContentID = P.PostID
            WHERE UCC.NUsername = ?
            ORDER BY P.ReleaseDate DESC
        """, (target,)):
            post_ids.append(p[0])
            posts.append([p[1], p[2]])

        for s in cur.execute("""
            SELECT S.StoryID, S.Content, S.UpTime
            FROM UserCreatesContent UCC
            JOIN Story S ON UCC.ContentID = S.StoryID
            WHERE UCC.NUsername = ?
            AND datetime(S.UpTime, '+1 day') > datetime('now')
            ORDER BY S.UpTime DESC
        """, (target,)):
            story_ids.append(s[0])
            stories.append([s[1], s[2]])

    layout = [
        [sg.Text("Username: " + target)],
        [sg.Text("Name: " + name)],
        [sg.Text("Description: " + adesc)],
        [sg.Text("Personal Information: " + info)],
        [sg.Text(f"Followers: {followers}   Following: {following}")],
        [sg.HorizontalSeparator()]
    ]

    if can_view_content:
        layout += [
            [sg.Text("Posts")],
            [sg.Table(posts, ["Description", "Date"], key="POSTS",
                      enable_events=True, select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                      auto_size_columns=True, num_rows=6)],
            [sg.Button("View Post")],

            [sg.Text("Stories")],
            [sg.Table(stories, ["Content", "Uploaded"], key="STORIES",
                      enable_events=True, select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                      auto_size_columns=True, num_rows=4)],
            [sg.Button("View Story")]
        ]
    else:
        layout += [
            [sg.Text("This account is private.")],
            [sg.Text("Follow this user to see posts and stories.")]
        ]

    layout.append([sg.Button("Back")])

    window = sg.Window("User Profile", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            connections_page(viewer)
            return
        elif event == "View Post" and values["POSTS"]:
            idx = values["POSTS"][0]
            pid = post_ids[idx]
            window.close()
            post_detail_page(pid, viewer)
            return
        elif event == "View Story" and values["STORIES"]:
            idx = values["STORIES"][0]
            sid = story_ids[idx]
            window.close()
            story_detail_page(sid, viewer)
            return
    window.close()

def comments(username):
    posts = []
    post_ids = []

    for post in cur.execute("""
        SELECT DISTINCT P.PostID, P.PostDescription, P.ReleaseDate, UCC.NUsername
        FROM Comment C
        JOIN Post P ON C.ComContentID = P.PostID
        JOIN UserCreatesContent UCC ON UCC.ContentID = P.PostID
        WHERE C.WriterUN = ?
        ORDER BY P.ReleaseDate DESC
    """, (username,)):
        post_ids.append(post[0])
        posts.append((post[3], post[1], post[2]))

    layout = [
        [sg.Text("Posts You Commented On")],
        [sg.Listbox(posts, size=(60, 10), key="COMMENTEDPOSTS")],
        [sg.Button("View My Comments"), sg.Button("Back")]
    ]

    window = sg.Window("Comments", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            interactions_page(username)
        elif event == "View My Comments":
            if values["COMMENTEDPOSTS"]:
                index = posts.index(values["COMMENTEDPOSTS"][0])
                user_comments_page(post_ids[index], username)
    window.close()

def user_comments_page(post_id, username):
    comments = []

    for com in cur.execute("""
        SELECT TextContent, ComDate
        FROM Comment
        WHERE ComContentID = ? AND WriterUN = ?
        ORDER BY ComDate
    """, (post_id, username)):
        comments.append((com[1], com[0]))

    layout = [
        [sg.Text("Your Comments on This Post")],
        [sg.Listbox(comments, size=(60, 10))],
        [sg.Button("Back")]
    ]

    window = sg.Window("My Comments", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            comments(username)
    window.close()

def home_page(username):
    post_ids = []
    post_rows = []

    story_ids = []
    story_rows = []

    for post in cur.execute("""
        SELECT P.PostID, UCC.NUsername, P.PostDescription, P.ReleaseDate
        FROM Follow F
        JOIN UserCreatesContent UCC ON F.FollowingUN = UCC.NUsername
        JOIN Post P ON UCC.ContentID = P.PostID
        WHERE F.FollowerUN = ?
        ORDER BY P.ReleaseDate DESC
    """, (username,)):
        post_ids.append(post[0])
        post_rows.append([post[1], post[2], post[3]])

    for s in cur.execute("""
        SELECT S.StoryID, UCC.NUsername, S.Content, S.UpTime
        FROM Story S
        JOIN UserCreatesContent UCC ON S.StoryID = UCC.ContentID
        JOIN Follow F ON UCC.NUsername = F.FollowingUN
        WHERE F.FollowerUN = ?
        AND datetime(S.UpTime, '+1 day') > datetime('now')
        ORDER BY S.UpTime DESC
    """, (username,)):
        story_ids.append(s[0])
        story_rows.append([s[1], s[2], s[3]])

    layout = [
        [sg.Text("Stories")],
        [sg.Table(
            values=story_rows,
            headings=["Owner", "Story Content", "Date"],
            col_widths=[15, 30, 18],
            auto_size_columns=False,
            justification="left",
            num_rows=5,
            key="STORIES",
            enable_events=True
        )],
        [sg.Button("View Story")],

        [sg.HorizontalSeparator()],

        [sg.Text("Posts")],
        [sg.Table(
            values=post_rows,
            headings=["Owner", "Description", "Date"],
            col_widths=[15, 30, 18],
            auto_size_columns=False,
            justification="left",
            num_rows=10,
            key="POSTS",
            enable_events=True
        )],
        [sg.Button("View Post"), sg.Button("Back")]
    ]

    window = sg.Window("Homepage", layout, finalize=True)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            user_page(username)
            return
        elif event == "View Post" and values["POSTS"]:
            idx = values["POSTS"][0]
            window.close()
            post_detail_page(post_ids[idx], username)
            return
        elif event == "View Story" and values["STORIES"]:
            idx = values["STORIES"][0]
            window.close()
            story_detail_page(story_ids[idx], username)
            return
    window.close()

def story_detail_page(story_id, username):
    text = ""
    date = ""
    owner = ""

    for row in cur.execute("""
        SELECT S.Content, S.UpTime, UCC.NUsername
        FROM Story S
        JOIN UserCreatesContent UCC ON S.StoryID = UCC.ContentID
        WHERE S.StoryID = ?
    """, (story_id,)):
        text, date, owner = row

    layout = [
        [sg.Text("Owner:", size=(10,1)), sg.Text(owner)],
        [sg.Text("Posted:", size=(10,1)), sg.Text(str(date))],
        [sg.HorizontalSeparator()],
        [sg.Text(text)],
        [sg.Button("Back")]
    ]

    window = sg.Window("Story", layout)

    while True:
        event, _ = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            home_page(username)
            return
    window.close()

def post_detail_page(post_id, username):
    desc = ""
    date = ""
    owner = ""
    likes = 0
    comments = []
    tags = []
    for row in cur.execute("""
        SELECT DISTINCT T.TaggedUN
        FROM Tag T
        JOIN Media M ON T.TagMediaID = M.MediaID
        WHERE M.PostID = ?
    """, (post_id,)):
        tags.append(row[0])

    cur.execute("""
        SELECT P.PostDescription, P.ReleaseDate, UCC.NUsername
        FROM Post P
        JOIN UserCreatesContent UCC ON P.PostID = UCC.ContentID
        WHERE P.PostID = ?
    """, (post_id,))
    desc, date, owner = cur.fetchone()

    likes = cur.execute(
        "SELECT COUNT(*) FROM Likes WHERE ContentID = ?", (post_id,)
    ).fetchone()[0]

    cur.execute("""
        SELECT 1 FROM Likes 
        WHERE ContentID=? AND NUsername=?
    """, (post_id, username))
    liked = cur.fetchone() is not None

    for row in cur.execute("""
        SELECT WriterUN, TextContent, ComDate
        FROM Comment
        WHERE ComContentID = ?
        ORDER BY ComDate
    """, (post_id,)):
        comments.append([row[0], row[1], row[2]])

    layout = [
        [sg.Text("Post Details")],
        [sg.Text("Owner:", size=(10,1)), sg.Text(owner)],
        [sg.Text("Date:", size=(10,1)), sg.Text(str(date))],
        [sg.Text("Likes:", size=(10,1)), sg.Text(str(likes), key="LIKECOUNT")],
        [sg.Text("Description:", size=(10,1)), sg.Text(desc)],
        [sg.Text("Tagged:", size=(10,1)), sg.Text(", ".join(tags) if tags else "None")],
        [sg.Text("Comments:")],
        [sg.Table(
            values=comments,
            headings=["User", "Comment", "Date"],
            col_widths=[15, 30, 15],
            auto_size_columns=False,
            justification="left",
            num_rows=8,
            key="COMMENTS"
        )],

        [sg.Input(key="newcomment", size=(45,1)), sg.Button("Add Comment")],
        [sg.Button("Unlike" if liked else "Like", key="likebutton"), sg.Button("Back")]
    ]

    window = sg.Window("Post Details", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            home_page(username)
            return
        elif event == "likebutton":
            if not liked:
                cur.execute(
                    "INSERT INTO Likes (ContentID, NUsername) VALUES (?, ?)",
                    (post_id, username)
                )
                con.commit()
                likes += 1
                liked = True
                window["likebutton"].update("Unlike")
            else:
                cur.execute(
                    "DELETE FROM Likes WHERE ContentID=? AND NUsername=?",
                    (post_id, username)
                )
                con.commit()
                likes -= 1
                liked = False
                window["likebutton"].update("Like")
            window["LIKECOUNT"].update(str(likes))
        elif event == "Add Comment":
            if values["newcomment"]:
                cur.execute("""
                    INSERT INTO Comment (CommentID, ComDate, TextContent, WriterUN, ComContentID)
                    VALUES (
                        (SELECT MAX(CommentID) + 1 FROM Comment),
                        DATE('now'),
                        ?, ?, ?     
                    )
                """, (values["newcomment"], username, post_id))

                con.commit()
                comments.append([username, values["newcomment"], datetime.date.today().isoformat()])
                window["COMMENTS"].update(comments)
                window["newcomment"].update("")
    window.close()

login()