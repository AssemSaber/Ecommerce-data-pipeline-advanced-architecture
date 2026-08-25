import os
import json
from datetime import datetime


def write_rejected_summary_to_json(df, table_name):

    file_path = r'H:\Atos\Logs\logJson.json'

    try:

        # 1. Get rejected records summary
        summary = (
            df.groupby("reason")
              .size()
              .to_dict()
        )

        print("SUMMARY:", summary)

        # 2. Add timestamp
        summary["written_at"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        print("SUMMARY WITH TIME:", summary)

        # 3. Read old JSON
        if os.path.exists(file_path):

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            if content.strip():
                result = json.loads(content)
            else:
                result = {}

        else:
            result = {}

        # print("OLD JSON:", result)

        # 4. Create list if table doesn't exist
        if table_name not in result:
            result[table_name] = []

        # 5. Add new execution
        result[table_name].append(summary)

        # print("NEW JSON:", result)

        # 6. Write JSON
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                result,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(f"{table_name} summary written successfully")

    except Exception as e:
        print(f"Error writing rejected summary: {e}")