
from model.security import generate_key, validate_key
import os
import sys

# Clear screen
os.system('cls' if os.name == 'nt' else 'clear')

print("="*50)
print("   🛠️  LVC MEDIA - KEY GENERATOR TOOL  🛠️")
print("="*50)

while True:
    print("\n1. Tạo key mới (Generate Key)")
    print("2. Kiểm tra key (Validate Key)")
    print("3. Thoát (Exit)")
    
    choice = input("\n👉 Chọn (1/2/3): ").strip()
    
    if choice == "1":
        count = input("Nhập số lượng key muốn tạo (Mặc định 1): ")
        try:
            n = int(count)
        except:
            n = 1
            
        print("\n🔑 DASCHBOARD KEYS:")
        print("-" * 30)
        for i in range(n):
            key = generate_key()
            print(f"Key #{i+1}: {key}")
        print("-" * 30)
        print("Done!")
        
    elif choice == "2":
        k = input("\nNhập key cần kiểm tra: ")
        is_valid = validate_key(k)
        if is_valid:
            print(f"✅ Key '{k}' là HỢP LỆ!")
        else:
            print(f"❌ Key '{k}' KHÔNG hợp lệ.")
            
    elif choice == "3":
        break
    else:
        print("Sai lệnh, thử lại.")
