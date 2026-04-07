import os
import glob

base_path = "ClinicaPrivadaWS/src/main/java/pe/edu/pucp"

files = glob.glob(f"{base_path}/**/*WS.java", recursive=True)

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "@Stateless" not in content:
        # Add import
        content = content.replace("import jakarta.jws.WebService;", "import jakarta.jws.WebService;\nimport jakarta.ejb.Stateless;")
        
        # Add annotation before @WebService
        content = content.replace("@WebService(", "@Stateless\n@WebService(")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Added @Stateless to {filepath}")
    else:
        print(f"Already has @Stateless: {filepath}")

