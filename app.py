import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from flask import Flask, Response, abort, flash, redirect, render_template, request, session, url_for


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(
    os.environ.get(
        "BIOGRAPHY_DATABASE_PATH",
        str(BASE_DIR / "data" / "biography.sqlite3"),
    )
)
BIOGRAPHY_SECTIONS = (
    (
        1,
        "الشاعرة والفنانة المسرحية",
        "فضيلة زيدان ناجي العامري شاعرة وفنانة مسرحية من الوجوه الأدبية والفنية البارزة في مدينة الديوانية. جمعت في مسيرتها بين الشعر الشعبي والمسرح والتمثيل والكتابة والإخراج والتدريب الفني، وقدمت مشاركات وأعمالًا أسهمت في إثراء المشهد الثقافي في المحافظة.\n\nوهي ابنة الفنان الرائد والمربي والرياضي الراحل زيدان ناجي العامري، الذي شجعها منذ بداياتها، وكانت تجربته امتدادًا لمدرسة فنية وأدبية عُرفت بالإبداع والعمل وخدمة المجتمع.",
    ),
    (
        2,
        "النشأة والدراسة",
        "ولدت فضيلة زيدان ناجي العامري عام 1956م في مدينة الديوانية، في منطقة الفاضلية. دخلت مدرسة الخنساء الابتدائية عام 1962–1963م، ثم درست في متوسطة الجمهورية للبنات عام 1968–1969م.\n\nوفي عام 1970–1971م التحقت بإعدادية التجارة المختلطة، وتخرجت فيها عام 1973–1974م، ولم تكمل دراستها الجامعية.",
    ),
    (
        3,
        "حياتها الوظيفية",
        "بدأت عملها الوظيفي عام 1974م في دائرة زراعة الديوانية، ثم انتقلت إلى المعهد الفني وتولت رئاسة هيئة التدقيق. وأحيلت إلى التقاعد عام 1989م وفق قانون الخدمة الذي شمل خدمة خمس عشرة سنة وثلاثة أطفال.",
    ),
    (
        4,
        "بداياتها في الشعر الشعبي",
        "بدأت محاولاتها الشعرية عام 1968م؛ فكانت تقرأ الشعر الشعبي وتحفظ القصائد وتكتب، قبل أن تتعرف إلى أوزانه. وحين لمس والدها حبها للشعر، شجعها وأهداها كتاب «ميزان الذهب»، فطورت كتاباتها تدريجيًا وبنت تجربتها الخاصة.\n\nعمل الشاعران كاظم خبط الجبوري وجبار سمير الحمداني معها في الدائرة نفسها، وأسهمَا في تعريفها بجمعية الشعراء الشعبيين في الديوانية. ومن خلال زياراتها للجمعية اكتسبت خبرات شعرية وثقافية.",
    ),
    (
        5,
        "المهرجانات والمنشورات",
        "شاركت عام 1972م في المهرجان القطري المقام في الديوانية إلى جانب عريان السيد خلف، وبشير العبودي، وكاظم الركابي، وكاظم خبط الجبوري، وجبار سمير الحمداني وغيرهم. وكانت من أوائل النساء اللواتي اعتلين منصة الشعر في المحافظة في تلك المرحلة.\n\nتوالت مشاركاتها في المهرجانات الشعرية في المحافظات العراقية، من شمال العراق إلى جنوبه، وفي بغداد. ونشرت قصائد لها في مجلة ألف باء وجريدة القادسية. وكتبت البوذيات والزهيري والدارمي والقصيدة والأغنية والأنشودة، مؤكدة استقلال تجربتها وعدم امتدادها إلى تجربة شاعر بعينه.",
    ),
    (
        6,
        "العضوية والتقدير",
        "كانت عضوًا في جمعية الشعراء الشعبيين في الديوانية واتحاد الشعراء الشعبيين ونقابة الفنانين. وشاركت في مهرجانات ومسابقات فردية وجماعية، وحققت مراتب متقدمة ونالت شهادات تقدير وتشكرات ودروعًا.\n\nومن الشعراء الذين عملت وشاركت معهم: جبار سمير الحمداني، وكاظم خبط الجبوري، وصاحب الضويري، وكامل الناصري، وكامل العامري، وعبد الإله العامري، وغيرهم.",
    ),
    (
        7,
        "بداياتها المسرحية",
        "بدأت فضيلة زيدان تجربتها المسرحية في المسرح الفلاحي، ثم شاركت في أعمال نقابة الفنانين والشباب والمسرح الجماهيري ومهرجانات نيبور والفرق الفنية. وكان من أوائل أعمالها مسرحية «صرخة في المزرعة» عام 1975م، من تأليف جبار سمير الحمداني وإخراج علي هادي الحسون.\n\nشارك في العمل هادي رديف وغسان الخزرجي ومهدي طالب الشرع وجبار سمير وحليمة رحمن وغيرهم. وبعد انقطاع طويل عن المسرح، عادت إلى النشاط الفني عام 2005م.",
    ),
    (
        8,
        "أبرز الأعمال المسرحية",
        "شاركت في أعمال مسرحية متعددة، منها: «أحلام بريئة» تأليف وإخراج توفيق عبد الواحد؛ «ليش» و«مساء التأمل» و«سليل الحق» و«الحسين خالدًا» و«أم أبيها» و«جاءت من نفر» تأليف وإخراج سعد هدابي؛ «سيدة البلدان» إعداد وإخراج رحيم ماجد؛ «سبي هنا وسبي هناك» تأليف وإخراج توفيق عبد الواحد؛ «الخروج من دائرة الجنون» عن نص أجنبي، إخراج خالد إيما؛ و«برلماني ولكن» و«المسخ» تأليف وإخراج حسين العراقي.\n\nومن أعمالها أيضًا «وينك يا ابن الديوانية» تأليف وإخراج صادق مرزوق؛ «البالون الطائر» تأليف عزي الوهاب وإخراج مهند إبراهيم العبيدي؛ «المفتاح» تأليف يوسف العاني وإخراج فائز ميران؛ «رحلة العذاب» إعداد وإخراج صلاح عبد الستار الربيعي؛ و«أوديب ملكًا» عن سوفوكليس، ترجمة طه حسين، وإخراج نبيل محمد الغريفي. كما شاركت في أوبريت «مهد الشمس» من تأليف جبار سمير وإخراج سعد هدابي.",
    ),
    (
        9,
        "التعاون الفني",
        "تعاونت خلال مسيرتها مع المخرجين والفنانين علي هادي الحسون، ورحيم ماجد، وسعد هدابي، وتوفيق عبد الواحد، ورجاء كاظم جودي. وشاركت في أعمال إلى جانب غسان الخزرجي وهادي رديف ومحسن هادي، وغيرهم.\n\nكما عملت مع رحيم ماجد، ويحيى داود، وحليم هاتف، وأمل جاسم، وصلاح الربيعي، وعبد الستار الربيعي، ومهند إبراهيم، ومهند العميدي، وخالد إيما، وقيصر الوائلي، ورضا طارش، وفؤاد ميران، ومؤيد طه، وإحسان عبد الله، ونبيل حسون، ومصطفى الهلالي، وعارف سلام، وفلاح إبراهيم، وأسماء صفاء، وأزهار العسلي، وسماح صباح، وفراس الشاروط، وبسام حسين، وأزهر وصي، وغيرهم.",
    ),
    (
        10,
        "أعمالها التلفزيونية",
        "شاركت في أعمال تلفزيونية، منها «ملامح الوجه الآخر» من إخراج رجاء كاظم جودي، ومشهد في مسلسل «وادي السلام»، ومسلسل «حكايات من داخل السور» على تلفزيون الغدير، إلى جانب تمثيليات وبرامج وأعمال فنية أخرى في فضائية الغدير.",
    ),
    (
        11,
        "التدريب والكتابة والإخراج",
        "عملت في التدريب المسرحي في منتدى شباب النهروان، وكتبت وأخرجت عددًا من الأعمال المسرحية. وامتدت اهتماماتها إلى إعداد الأوبريتات وكتابة الأناشيد والأغاني، ومسرح الدمى، والأعمال اليدوية، وإقامة المعارض الفنية، وتدريب الشباب على العمل المسرحي.\n\nحققت أعمالها في المنتديات مراكز متقدمة، من بينها المركز الأول في عدد من المشاركات.",
    ),
    (
        12,
        "تجربة متعددة المواهب",
        "جمعت فضيلة زيدان العامري بين الشعر الشعبي والمسرح والتمثيل والكتابة والإخراج والتدريب والفنون اليدوية. وأسهم حضورها في مرحلة مهمة من الحركة الشعرية والمسرحية في الديوانية، حين كان حضور المرأة على المنصات أقل مما هو عليه اليوم.\n\nومنذ بداياتها في الديوانية ومشاركاتها في المهرجانات، إلى أعمالها على خشبة المسرح والتلفزيون والتدريب، كرست جانبًا كبيرًا من حياتها لخدمة الثقافة والفن، وقدمت صورة مشرقة للمرأة الديوانية المبدعة. وتبقى تجربتها شاهدًا على جيل من المبدعين الذين تركوا أثرهم في ذاكرة المدينة والحركة الثقافية والفنية العراقية.",
    ),
)

POEM_CATEGORIES = ("شعر", "أبوذية")
GALLERY_PHOTOS = (
    ("archive-01.png", "لقطة أرشيفية من عرض مسرحي", "من ذاكرة المسرح الديواني · ١"),
    ("archive-02.png", "لقطة أرشيفية من عرض مسرحي", "من ذاكرة المسرح الديواني · ٢"),
    ("archive-03.png", "لقطة أرشيفية من عرض مسرحي", "من ذاكرة المسرح الديواني · ٣"),
    ("archive-04.png", "لقطة أرشيفية من عرض مسرحي", "من ذاكرة المسرح الديواني · ٤"),
    ("archive-05.png", "لقطة أرشيفية من عرض مسرحي", "من ذاكرة المسرح الديواني · ٥"),
    ("archive-06.png", "لقطة أرشيفية من عرض مسرحي", "من ذاكرة المسرح الديواني · ٦"),
    ("archive-07.png", "لقطة أرشيفية من عرض مسرحي", "من ذاكرة المسرح الديواني · ٧"),
    ("archive-08.png", "لقطة أرشيفية من عرض مسرحي", "من ذاكرة المسرح الديواني · ٨"),
    ("archive-09.png", "صورة شخصية للفنانة فضيلة زيدان العامري", "فضيلة زيدان العامري"),
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get(
    "SESSION_COOKIE_SECURE", ""
).lower() in {"1", "true", "yes"}


def create_csrf_token():
    token = session.get("csrf_token")
    if token is None:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def validate_csrf_token():
    expected_token = session.get("csrf_token", "")
    submitted_token = request.form.get("csrf_token", "")
    if not expected_token or not secrets.compare_digest(expected_token, submitted_token):
        abort(400, description="تعذر التحقق من الطلب. أعد تحميل الصفحة وحاول مجددًا.")


def is_admin():
    return session.get("is_admin") is True


@contextmanager
def connect_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database():
    with connect_database() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS biography (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                name TEXT NOT NULL,
                birth_date TEXT NOT NULL DEFAULT '',
                birth_place TEXT NOT NULL DEFAULT ''
            )
            """
        )
        connection.execute(
            "INSERT OR IGNORE INTO biography (id, name) VALUES (1, ?)",
            ("فضيلة العامري",),
        )
        connection.execute(
            "UPDATE biography SET birth_place = ? WHERE id = 1 AND birth_place = ''",
            ("الديوانية، العراق",),
        )
        connection.execute(
            "UPDATE biography SET name = ? WHERE id = 1 AND name = ?",
            ("فضيلة زيدان ناجي العامري", "فضيلة العامري"),
        )
        connection.execute(
            "UPDATE biography SET birth_place = ? WHERE id = 1 AND birth_place = ?",
            ("الديوانية، الفاضلية", "الديوانية، العراق"),
        )
        connection.execute(
            "UPDATE biography SET birth_date = '' WHERE id = 1 AND substr(birth_date, 1, 4) != ?",
            ("1956",),
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS biography_sections (
                id INTEGER PRIMARY KEY,
                heading TEXT NOT NULL,
                body TEXT NOT NULL
            )
            """
        )
        connection.executemany(
            """
            INSERT INTO biography_sections (id, heading, body) VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                heading = excluded.heading,
                body = excluded.body
            """,
            BIOGRAPHY_SECTIONS,
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS poetry_entries (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                excerpt TEXT NOT NULL,
                body TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "UPDATE poetry_entries SET category = ? WHERE category NOT IN (?, ?)",
            (POEM_CATEGORIES[0], *POEM_CATEGORIES),
        )


def read_biography():
    with connect_database() as connection:
        return connection.execute(
            "SELECT name, birth_date, birth_place FROM biography WHERE id = 1"
        ).fetchone()


def read_biography_sections():
    with connect_database() as connection:
        return connection.execute(
            "SELECT id, heading, body FROM biography_sections ORDER BY id"
        ).fetchall()


def read_poetry_entries():
    with connect_database() as connection:
        return connection.execute(
            "SELECT id, title, category, excerpt, body FROM poetry_entries ORDER BY id"
        ).fetchall()


def calculate_age(birth_date):
    if not birth_date:
        return None
    try:
        born = date.fromisoformat(birth_date)
    except ValueError:
        return None
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def public_base_url():
    return (
        os.environ.get("SITE_URL")
        or os.environ.get("RENDER_EXTERNAL_URL")
        or request.url_root
    ).rstrip("/")


@app.route("/robots.txt")
def robots_txt():
    sitemap_url = f"{public_base_url()}{url_for('sitemap_xml')}"
    return Response(
        f"User-agent: *\nAllow: /\nSitemap: {sitemap_url}\n",
        mimetype="text/plain",
    )


@app.route("/google3b12ec2b77f8bead.html")
def google_site_verification():
    return Response(
        "google-site-verification: google3b12ec2b77f8bead.html",
        mimetype="text/plain",
    )


@app.route("/sitemap.xml")
def sitemap_xml():
    page_url = escape(f"{public_base_url()}{url_for('biography_page')}")
    return Response(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<url><loc>{page_url}</loc></url>"
        "</urlset>",
        mimetype="application/xml",
    )


@app.route("/", methods=["GET", "POST"])
def biography_page():
    if request.method == "POST":
        if not is_admin():
            flash("يلزم تسجيل دخول الإدارة لتعديل السيرة.", "error")
            return redirect(url_for("admin_login"))
        validate_csrf_token()

        name = request.form.get("name", "").strip()
        birth_date = request.form.get("birth_date", "").strip()
        birth_place = request.form.get("birth_place", "").strip()

        if not name:
            flash("يرجى كتابة اسم الشاعرة.", "error")
            return redirect(url_for("biography_page"))

        if birth_date:
            try:
                parsed_birth_date = date.fromisoformat(birth_date)
            except ValueError:
                flash("يرجى إدخال تاريخ ميلاد صحيح.", "error")
                return redirect(url_for("biography_page"))
            if parsed_birth_date > date.today():
                flash("لا يمكن أن يكون تاريخ الميلاد في المستقبل.", "error")
                return redirect(url_for("biography_page"))

        with connect_database() as connection:
            connection.execute(
                """
                UPDATE biography
                SET name = ?, birth_date = ?, birth_place = ?
                WHERE id = 1
                """,
                (name, birth_date, birth_place),
            )
        flash("حُفظت بيانات السيرة بنجاح.", "success")
        return redirect(url_for("biography_page"))

    profile = read_biography()
    age = calculate_age(profile["birth_date"])
    sections = read_biography_sections()
    poems = read_poetry_entries()
    default_poem_category = poems[0]["category"] if poems else POEM_CATEGORIES[0]
    site_url = f"{public_base_url()}{url_for('biography_page')}"
    return render_template(
        "index.html",
        profile=profile,
        age=age,
        sections=sections,
        poems=poems,
        default_poem_category=default_poem_category,
        poem_categories=POEM_CATEGORIES,
        gallery_photos=GALLERY_PHOTOS,
        is_admin=is_admin(),
        is_static_site=app.config.get("STATIC_SITE_BUILD", False),
        csrf_token=create_csrf_token(),
        site_url=site_url,
        site_image_url=f"{public_base_url()}{url_for('static', filename='portrait.png')}",
        structured_data={
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "WebSite",
                    "name": "فضيلة العامري",
                    "url": site_url,
                    "inLanguage": "ar",
                },
                {
                    "@type": "Person",
                    "name": profile["name"],
                    "alternateName": ["فضيلة العامري", "فضيلة زيدان العامري"],
                    "url": site_url,
                    "image": f"{public_base_url()}{url_for('static', filename='portrait.png')}",
                    "description": "الشاعرة والفنانة المسرحية العراقية فضيلة زيدان ناجي العامري من الديوانية.",
                    "jobTitle": ["شاعرة", "فنانة مسرحية", "كاتبة", "مخرجة"],
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": profile["birth_place"] or "الديوانية",
                        "addressCountry": "العراق",
                    },
                    "knowsAbout": ["الشعر الشعبي العراقي", "المسرح", "التمثيل"],
                },
            ],
        },
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    admin_password = os.environ.get("ADMIN_PASSWORD", "")
    if not admin_password:
        return render_template("admin_login.html", configured=False), 503

    if request.method == "POST":
        validate_csrf_token()
        submitted_password = request.form.get("password", "")
        if secrets.compare_digest(admin_password, submitted_password):
            session.clear()
            session["is_admin"] = True
            create_csrf_token()
            flash("تم تسجيل دخول الإدارة بنجاح.", "success")
            return redirect(url_for("biography_page"))
        flash("كلمة المرور غير صحيحة.", "error")

    return render_template(
        "admin_login.html",
        configured=True,
        csrf_token=create_csrf_token(),
    )


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    if not is_admin():
        return redirect(url_for("biography_page"))
    validate_csrf_token()
    session.clear()
    flash("تم تسجيل خروج الإدارة.", "success")
    return redirect(url_for("biography_page"))


@app.route("/admin/poems", methods=["POST"])
def add_poem():
    if not is_admin():
        flash("يلزم تسجيل دخول الإدارة لإضافة قصيدة.", "error")
        return redirect(url_for("admin_login"))
    validate_csrf_token()

    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip()
    excerpt = request.form.get("excerpt", "").strip()
    body = request.form.get("body", "").strip()

    if not all((title, category, excerpt, body)):
        flash("يرجى تعبئة عنوان القصيدة وتصنيفها ومقتطفها ونصها.", "error")
        return redirect(url_for("biography_page") + "#poems")
    if category not in POEM_CATEGORIES:
        flash("يرجى اختيار «شعر» أو «أبوذية» تصنيفًا للقصيدة.", "error")
        return redirect(url_for("biography_page") + "#poems")
    if len(title) > 160 or len(category) > 60 or len(excerpt) > 240 or len(body) > 12000:
        flash("تجاوز أحد الحقول الحد الأقصى المسموح به.", "error")
        return redirect(url_for("biography_page") + "#poems")

    with connect_database() as connection:
        connection.execute(
            """
            INSERT INTO poetry_entries (title, category, excerpt, body)
            VALUES (?, ?, ?, ?)
            """,
            (title, category, excerpt, body),
        )
    flash("أُضيفت القصيدة بنجاح.", "success")
    return redirect(url_for("biography_page") + "#poems")


initialize_database()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)