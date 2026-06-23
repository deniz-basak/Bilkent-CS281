--
-- File generated with SQLiteStudio v3.4.17 on Tue Jun 23 10:23:50 2026
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: AdminAccount
CREATE TABLE AdminAccount (
    AUsername VARCHAR (20) NOT NULL,
    PRIMARY KEY (
        AUsername
    ),
    FOREIGN KEY (
        AUsername
    )
    REFERENCES User (Username) 
);

INSERT INTO AdminAccount (AUsername) VALUES ('neuraldsp');
INSERT INTO AdminAccount (AUsername) VALUES ('wysteria.official');
INSERT INTO AdminAccount (AUsername) VALUES ('thornhill.melb');
INSERT INTO AdminAccount (AUsername) VALUES ('loathe');
INSERT INTO AdminAccount (AUsername) VALUES ('opeth.official');

-- Table: Comment
CREATE TABLE Comment (
    CommentID    INTEGER      NOT NULL,
    ComDate      NUMERIC,
    TextContent  VARCHAR (50) NOT NULL,
    WriterUN     VARCHAR (20) NOT NULL,
    ComContentID INTEGER      NOT NULL,
    PRIMARY KEY (
        CommentID
    ),
    FOREIGN KEY (
        WriterUN
    )
    REFERENCES UserAccount (NUsername),
    FOREIGN KEY (
        ComContentID
    )
    REFERENCES UserCreatesContent (ContentID) ON DELETE CASCADE
);


-- Table: Follow
CREATE TABLE Follow (
    FollowerUN  VARCHAR (20) NOT NULL,
    FollowingUN VARCHAR (20) NOT NULL,
    PRIMARY KEY (
        FollowerUN,
        FollowingUN
    ),
    FOREIGN KEY (
        FollowerUN
    )
    REFERENCES UserAccount (NUsername),
    FOREIGN KEY (
        FollowingUN
    )
    REFERENCES UserAccount (NUsername) 
);


-- Table: Likes
CREATE TABLE Likes (
    ContentID INTEGER      NOT NULL,
    NUsername VARCHAR (20) NOT NULL,
    PRIMARY KEY (
        ContentID,
        NUsername
    ),
    FOREIGN KEY (
        ContentID
    )
    REFERENCES UserCreatesContent (ContentID) ON DELETE CASCADE,
    FOREIGN KEY (
        NUsername
    )
    REFERENCES UserAccount (NUsername) 
);


-- Table: Media
CREATE TABLE Media (
    MediaID    INTEGER      NOT NULL,
    Resolution VARCHAR (20),
    PostID     INTEGER      NOT NULL,
    PRIMARY KEY (
        MediaID
    ),
    FOREIGN KEY (
        PostID
    )
    REFERENCES Post (PostID) ON DELETE CASCADE
);


-- Table: Photo
CREATE TABLE Photo (
    PhotoID INTEGER NOT NULL
                  REFERENCES Media (MediaID) ON DELETE CASCADE,
    PRIMARY KEY (
        PhotoID
    ),
    FOREIGN KEY (
        PhotoID
    )
    REFERENCES Media (MediaID) ON DELETE CASCADE
);


-- Table: Post
CREATE TABLE Post (
    PostID          INTEGER      NOT NULL,
    PostDescription VARCHAR (50),
    ReleaseDate     NUMERIC,
    PRIMARY KEY (
        PostID
    ),
    FOREIGN KEY (
        PostID
    )
    REFERENCES UserCreatesContent (ContentID) ON DELETE CASCADE
);


-- Table: Story
CREATE TABLE Story (
    StoryID INTEGER       NOT NULL,
    Content VARCHAR (100),
    UpTime  NUMERIC,
    PRIMARY KEY (
        StoryID
    ),
    FOREIGN KEY (
        StoryID
    )
    REFERENCES UserCreatesContent (ContentID) 
);


-- Table: Tag
CREATE TABLE Tag (
    TaggedUN   VARCHAR (20) NOT NULL,
    TagMediaID VARCHAR (20) NOT NULL,
    PRIMARY KEY (
        TaggedUN,
        TagMediaID
    ),
    FOREIGN KEY (
        TaggedUN
    )
    REFERENCES UserAccount (NUsername),
    FOREIGN KEY (
        TagMediaID
    )
    REFERENCES Media (MediaID) ON DELETE CASCADE
);


-- Table: User
CREATE TABLE User (
    Username VARCHAR (20) NOT NULL,
    Name     VARCHAR (20),
    Surname  VARCHAR (20),
    Password VARCHAR (30) NOT NULL,
    PRIMARY KEY (
        Username
    )
);

INSERT INTO User (Username, Name, Surname, Password) VALUES ('opeth.official', 'Opeth', 'Official', 'so.rrow');
INSERT INTO User (Username, Name, Surname, Password) VALUES ('loathe', 'Loathe', 'The Band', 'is.it.rll.u?');
INSERT INTO User (Username, Name, Surname, Password) VALUES ('thornhill.melb', 'Thornhill', 'Official', 'silver_swarm3');
INSERT INTO User (Username, Name, Surname, Password) VALUES ('thom.yorke', 'Thom', 'Yorke', 'ok.computer');
INSERT INTO User (Username, Name, Surname, Password) VALUES ('wysteria.official', 'Wysteria', 'Official', 'un_named');
INSERT INTO User (Username, Name, Surname, Password) VALUES ('misha.mansoor', 'Misha', 'Mansoor', 'peripheral');
INSERT INTO User (Username, Name, Surname, Password) VALUES ('neuraldsp', 'Neural', 'DSP', 'djent123');
INSERT INTO User (Username, Name, Surname, Password) VALUES ('buster.ode', 'Buster', 'Odeholm', 'vildhjarta');
INSERT INTO User (Username, Name, Surname, Password) VALUES ('silentgarrett', 'Garrett', 'Russel', 'antimatter8');
INSERT INTO User (Username, Name, Surname, Password) VALUES ('inventmrcs', 'Marcus', 'Vik', 'shade.astray');

-- Table: UserAccount
CREATE TABLE UserAccount (
    NUsername      VARCHAR (20) NOT NULL,
    AccDescription VARCHAR (50),
    Location       VARCHAR (50),
    AccountPrivacy NUMERIC      NOT NULL,
    PRIMARY KEY (
        NUsername
    ),
    FOREIGN KEY (
        NUsername
    )
    REFERENCES User (Username) 
);

INSERT INTO UserAccount (NUsername, AccDescription, Location, AccountPrivacy) VALUES ('misha.mansoor', 'djent is not a genre', 'USA', 0);
INSERT INTO UserAccount (NUsername, AccDescription, Location, AccountPrivacy) VALUES ('thom.yorke', 'paranoid android', 'USA', 1);
INSERT INTO UserAccount (NUsername, AccDescription, Location, AccountPrivacy) VALUES ('buster.ode', 't h a l l', 'Norway', 0);
INSERT INTO UserAccount (NUsername, AccDescription, Location, AccountPrivacy) VALUES ('silentgarrett', 'SUPERBLOOM OUT NOW!', 'USA', 1);
INSERT INTO UserAccount (NUsername, AccDescription, Location, AccountPrivacy) VALUES ('inventmrcs', 'I scream and sing', 'Sweden', 1);

-- Table: UserCreatesContent
CREATE TABLE UserCreatesContent (
    ContentID   INTEGER      NOT NULL,
    ContentLink VARCHAR (20) UNIQUE,
    NUsername   VARCHAR (20) NOT NULL,
    PRIMARY KEY (
        ContentID
    ),
    FOREIGN KEY (
        NUsername
    )
    REFERENCES UserAccount (NUsername) 
);


-- Table: Video
CREATE TABLE Video (
    VideoID  INTEGER NOT NULL
                     UNIQUE
                     REFERENCES Media (MediaID) ON DELETE CASCADE,
    Duration NUMERIC,
    PRIMARY KEY (
        VideoID
    ),
    FOREIGN KEY (
        VideoID
    )
    REFERENCES Media (MediaID) ON DELETE CASCADE
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
