import csv

# Load industries.csv to get available industry values
def load_industries():
    try:
        industries = []
        with open('industries.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) > 0 and row[0].strip():  # Skip empty values
                    industries.append(row[0].strip())
        
        # Remove duplicates and sort
        industries = sorted(list(set(industries)))
        return "AVAILABLE INDUSTRIES:\n" + ", ".join(industries) + "\n"
    except Exception as e:
        return f"Error loading industries: {str(e)}\n"

# Load sectors.csv to get available sector values
def load_sectors():
    try:
        sectors = []
        with open('sectors.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) > 0 and row[0].strip():  # Skip empty values
                    sectors.append(row[0].strip())
        
        # Remove duplicates and sort
        sectors = sorted(list(set(sectors)))
        return "AVAILABLE SECTORS:\n" + ", ".join(sectors) + "\n"
    except Exception as e:
        return f"Error loading sectors: {str(e)}\n"

# Load sizes.csv to get available size values  
def load_sizes():
    try:
        sizes = []
        with open('sizes.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) > 0 and row[0].strip():  # Skip empty values
                    sizes.append(row[0].strip())
        
        # Remove duplicates and maintain order
        seen = set()
        unique_sizes = []
        for size in sizes:
            if size not in seen:
                seen.add(size)
                unique_sizes.append(size)
        
        return "AVAILABLE SIZES (scalemarketcap):\n" + ", ".join(unique_sizes) + "\n"
    except Exception as e:
        return f"Error loading sizes: {str(e)}\n"

# Load examples.csv to get example prompts and responses
def load_examples():
    try:
        examples_str = "EXAMPLES OF USER QUERIES AND SQL RESPONSES:\n\n"
        with open('examples.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) >= 2:
                    prompt = row[0].strip()
                    response = row[1].strip()
                    examples_str += f"User: {prompt}\nSQL: {response}\n\n"
        return examples_str
    except Exception as e:
        return f"Error loading examples: {str(e)}\n"

# Load indicators.csv and create database schema description
def load_database_schema():
    try:
        schema_description = "DATABASE SCHEMA AND AVAILABLE INDICATORS:\n\n"
        schema_description += "Main Tables:\n"
        schema_description += "- TICKERS: Company information (ticker, company_name, exchange, sector, industry, scalemarketcap)\n"
        schema_description += "- All indicator tables have columns: ticker, date, and the indicator value\n\n"
        schema_description += "Available Indicators:\n"
        
        with open('indicators.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) >= 3:
                    indicator = row[0].strip()
                    table_name = row[1].strip()
                    description = row[2].strip()
                    schema_description += f"- {indicator}: {description} (table: {table_name})\n"
        
        return schema_description
    except Exception as e:
        return f"Error loading schema: {str(e)}"

# Load system prompt from file
def load_system_prompt_template():
    try:
        with open('system_prompt.txt', 'r') as file:
            return file.read()
    except Exception as e:
        return f"Error loading system prompt: {str(e)}"

# Main function to get complete system prompt
def get_system_prompt():
    """Returns the complete system prompt with all data loaded and formatted."""
    # Load all components
    database_schema = load_database_schema()
    examples = load_examples()
    industries = load_industries()
    sectors = load_sectors()
    sizes = load_sizes()
    system_prompt_template = load_system_prompt_template()
    
    # Format and return the complete system prompt
    return system_prompt_template.format(database_schema, examples, industries, sectors, sizes)