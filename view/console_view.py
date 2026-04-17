class ConsoleView:
    def show_welcome(self):
        print("=========================================")
        print("      AUTO WORDPRESS POST GEN TOOL       ")
        print("=========================================")

    def get_user_input(self):
        print("\nPlease enter the article details:")
        title = input("Article Title: ")
        video_url = input("Video Link: ")
        image_url = input("Image URL/Path: ")
        return title, video_url, image_url

    def get_wp_credentials(self):
        print("\n--- WP Configuration (Mock) ---")
        url = input("Site URL (e.g., https://mysite.com): ")
        user = input("Username: ")
        pwd = input("App Password: ")
        return url, user, pwd

    def show_success(self, title):
        print(f"\n[SUCCESS] Post '{title}' has been successfully created!")

    def show_error(self, message):
        print(f"\n[ERROR] {message}")
