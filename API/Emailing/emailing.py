import smtplib
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import dotenv_values


def send_email(host, port, from_email, password, to_email, subject, message):
    smtp = smtplib.SMTP(host, port)
    smtp.starttls()
    smtp.login(from_email, password)

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    smtp.send_message(msg)
    smtp.quit()


env_vars = dotenv_values(".env")

HOST = env_vars.get("HOST")
PORT = env_vars.get("PORT")
FROM_EMAIL = env_vars.get("FROM_EMAIL")
GOOGLE_APP_PASSWORD = env_vars.get("GOOGLE_APP_PASSWORD")
TO_EMAIL = "a@yahoo.ro"
SUBJECT = "Welcome to the Exciting World of Chess on Chess.ro!"
MESSAGE = '''Greetings and welcome to Chess.ro, your new home for all things chess! We're thrilled to have you join 
our vibrant community of chess enthusiasts, from seasoned grandmasters to passionate beginners like yourself.

Whether you're a seasoned tactician or just learning the first moves, we're here to provide you with a rich and 
rewarding chess experience. Here's a glimpse of what awaits you on our platform:

1. Play Chess Anytime, Anywhere:
    - Engage in live chess matches against players of similar skill levels using our intuitive matchmaking system.
    - Challenge your friends to a private game and test your strategies against familiar faces.
    - Explore our extensive archive of past games played by renowned masters and analyze the intricacies of their moves.

2. Hone Your Skills and Climb the Ranks:
    - Practice your tactics and opening strategies with our interactive puzzles and training modules.
    - Learn from engaging chess lessons and tutorials tailored to different skill levels.
    - Participate in tournaments and competitions to test your skills and climb the leaderboard.

3. Connect with the Chess Community:
    - Join our active forums to discuss chess strategies, share game analysis, and learn from other players.
    - Connect with fellow chess enthusiasts through private messaging and public chat rooms.
    - Expand your chess network by participating in online chess clubs and forming study groups.

4. Additional Resources: - Explore our comprehensive library of chess articles and ebooks covering various aspects of 
the game, from historical insights to advanced endgame techniques. - Watch instructional videos and live streams by 
renowned chess experts and learn from their insights. - Stay updated on the latest chess news and events through our 
integrated news feed.

Beyond the features mentioned above, we're constantly striving to improve your experience by:
    - Implementing new and exciting game modes and challenges.
    - Providing additional learning resources and tools.
    - Enhancing the platform's user interface and accessibility.

We encourage you to explore everything Chess has to offer and customize your journey based on your preferences and 
goals. As you embark on this exciting chess adventure, remember: - Chess is a lifelong journey of learning and 
improvement. Embrace the challenge, learn from your mistakes, and never stop exploring the depths of this remarkable 
game. - The Chess community is here to support you every step of the way. Don't hesitate to ask questions, 
seek advice, and engage with other players. - Most importantly, have fun! Chess is a game of strategy, but it's also 
a game of enjoyment. So relax, have fun, and let the joy of chess take over.

Welcome once again to Chess.ro. We wish you all the best on your chess journey!'''

send_email(HOST, PORT, FROM_EMAIL, GOOGLE_APP_PASSWORD, TO_EMAIL, SUBJECT, MESSAGE)


async def send_email_with_attachment(host, port, from_email, password, to_email, subject, message, attachment=None):
    try:
        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls()
            smtp.login(from_email, password)

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            if attachment:
                attachment_mime = MIMEApplication(attachment.getvalue(), _subtype="octet-stream")
                attachment_mime.add_header('Content-Disposition', 'attachment', filename='qrcode.png')
                msg.attach(attachment_mime)

            smtp.send_message(msg)
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
