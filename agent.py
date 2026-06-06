from google.adk.agents.llm_agent import Agent
import pymysql
from pymysql import Connection

def connect_database() -> Connection:
    return pymysql.connect(
        host='localhost',       # 数据库地址
        port=3306,
        user='<user name>',      # 数据库用户名
        password='<password>',    # 数据库密码
        database='<database>',    # 数据库名称
        charset='utf8mb4',      # 编码格式
        cursorclass=pymysql.cursors.DictCursor # 以字典形式返回结果
    )

# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

def read_mysql(news_id: int) -> dict:
    print(f"search news_id {news_id}")
    connection = connect_database()
    try:
        with connection.cursor() as cursor:
            # 2. 执行 SQL 查询
            sql = f"SELECT `news_id`, `title`, `content`, `is_soccer`, `is_good_news` FROM `<table name>` WHERE news_id = {news_id}"
            cursor.execute(sql)
        
            # 3. 获取所有查询结果
            result = cursor.fetchall()
            # for row in result:
                # print("id = ", row['news_id'], " title = ", row['title'], " content = ", row['content'], " is_soccer = ", row['is_soccer'], " is_good_news = ", row['is_good_news'])
    finally:
        # 4. 关闭连接
        connection.close()
    return result
    
def update(news_id: int, is_soccer: bool, is_good_news: bool):
    connection = connect_database()
    print(f"update {news_id}, {is_soccer}, {is_good_news}")
    if is_soccer is None:
        is_soccer = 'null'
    if is_good_news is None:
        is_good_news = 'null'
    try:
        with connection.cursor() as cursor:
            # 2. 执行 SQL 查询
            sql = f"UPDATE <table name> SET is_soccer={is_soccer}, is_good_news={is_good_news} WHERE news_id={news_id}"
            cursor.execute(sql)
        
            # 3. 获取所有查询结果
            result = cursor.fetchall()
            # for row in result:
                # print("id = ", row['news_id'], " title = ", row['title'], " content = ", row['content'], " is_soccer = ", row['is_soccer'], " is_good_news = ", row['is_good_news'])
        connection.commit()
    finally:
        # 4. 关闭连接
        connection.close()

"""
update(1, None, None)
result = read_mysql(1)
for row in result:
    print("id = ", row['news_id'], " is_soccer = ", row['is_soccer'], " is_good_news = ", row['is_good_news'])


"""

root_agent = Agent(
    model='gemini-flash-latest',
    name='root_agent',
    description="Tells the current time in a specified city.",
    instruction="""
# Role
You are an efficient and precise data classification and processing Agent, serving as a core component in an automated data pipeline. Your task is to read news records from a database, analyze their content, and update the processing results.

# Tools
You have access to and must strictly use the following two tools:
1. `read_mysql(news_id: int)`: Used to retrieve data from the database using the provided news ID. Returns data in the format: `{"news_id": int, "title": str, "content": str}`.
2. `update(news_id: int, is_soccer: bool, is_good_news: bool)`: Used to write the analysis results back to the database.

# Workflow
When a user provides a `news_id`, you must strictly follow this 3-step execution chain:

**Step 1: Retrieve**
Immediately call the `read_mysql(news_id)` tool to retrieve the `title` and `content` of the news. Do not make any assumptions or judgments before receiving the tool's response.

**Step 2: Analyze**
Based on the retrieved title and content, evaluate the text across the following two dimensions:
- **Dimension A: Is it related to soccer? (`is_soccer`)**
  - **True**: The content explicitly involves soccer / association football (including but not limited to: soccer clubs, soccer players, managers/coaches, tournaments like the World Cup or top European leagues, match scores, transfers, the pitch, etc.).
  - **False**: The content relates to other sports (e.g., basketball, American football), non-sports news, or completely unrelated fields.
- **Dimension B: Is it good news or bad news? (`is_good_news`)**
  - **True (Good news / Positive development)**: Involves winning, advancing to next rounds, successful transfers/signings, players recovering from injuries, securing sponsorships, breaking records, winning awards, etc. *(Note: If the news is objectively neutral and lacks obvious negative events, default to True).*
  - **False (Bad news / Negative development)**: Involves losing matches, elimination, player injuries, managers getting sacked/fired, scandals, fines, relegation, financial crises, etc.

**Step 3: Update**
Based on the analysis results from Step 2, call the `update(news_id, is_soccer, is_good_news)` tool to write the final classification back to the database.

# Constraints & Rules
1. **No Hallucinations**: You are strictly forbidden from guessing or fabricating the news content without successfully calling the `read_mysql` tool first.
2. **Strict Sequence**: You must wait for the payload from `read_mysql` to return before you are allowed to call the `update` tool.
3. **Objective Stance**: When determining "good vs. bad news," base your judgment entirely on the objective nature of the event itself (e.g., a player injury is universally classified as bad news). Do not adopt the subjective bias of any specific team's fan base.
4. **Silent Execution**: After successfully calling the `update` tool, output a brief confirmation message to the user (e.g., "News ID [news_id] processed: [Soccer Related: Yes/No], [Good News: Yes/No]"). Do not output your internal reasoning or thinking process.
   
""",
   tools=[read_mysql, update]
)

