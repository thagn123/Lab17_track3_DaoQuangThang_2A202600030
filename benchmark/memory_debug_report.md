# 🔍 Multi-Memory Debug Report

Giải thích chi tiết về dữ liệu đang được lưu trữ trong từng ngăn nhớ.

## 1. Long-term Memory (User Facts & Preferences)
> **Nơi lưu:** Redis (hoặc Dictionary RAM nếu fallback). Dùng để cá nhân hóa lâu dài.

### 👤 User Facts
- The user has a hobby of hiking.
- User prefers React for frontend development.
- User prefers using Python for backend development.
- User prefers Python for backend development.
- User is from Vietnam.
- User's name is Bob.
- User prefers Dark Mode for their UI theme.
- User prefers using React for frontend development.
- User loves hiking.
- User is a software engineer.
- User likes Dark Mode.
- The user has a job related to software engineering or development.
- The user is interested in hiking routes in Vietnam.
- The user fixed a production bug by increasing the database connection pool size and adding retry logic in the API layer.

### ⚙️ User Preferences
*Trống*

## 2. Episodic Memory (Learning from Experience)
> **Nơi lưu:** ChromaDB. Dùng để nhớ lại cách giải quyết các vấn đề tương tự trong quá khứ.

### Episode 1: How did we handle the production bug yesterday?
- **Outcome:** Success
- **Reflection:** *The agent provided a clear and concise explanation of how the production bug was handled, detailing the specific actions taken to resolve the issue. The agent also offered further assistance, indicating a proactive approach to customer service.*
- **Importance Score:** 0.7
- **Trajectory Snapshot:** ['How did we handle the production bug yesterday?', 'Yesterday, we handled the production bug by increasing the database connection pool size and addi...

### Episode 2: How did we handle the production bug yesterday?
- **Outcome:** Success
- **Reflection:** *The agent provided a clear and concise explanation of how the production bug was handled, detailing the specific actions taken (increasing database connection pool size and adding retry logic). The agent also offered further assistance, indicating a proactive approach to customer service.*
- **Importance Score:** 0.7
- **Trajectory Snapshot:** ['How did we handle the production bug yesterday?', 'Yesterday, we handled the production bug by increasing the database connection pool size and addi...

### Episode 3: How did we handle the production bug yesterday?
- **Outcome:** Success
- **Reflection:** *The agent provided a clear and concise explanation of how the production bug was handled, detailing the specific actions taken (increasing database connection pool size and adding retry logic). The agent also offered further assistance, indicating a proactive approach to user support.*
- **Importance Score:** 0.7
- **Trajectory Snapshot:** ['How did we handle the production bug yesterday?', 'Yesterday, we handled the production bug by increasing the database connection pool size and addi...

### Episode 4: How did we handle the production bug yesterday?
- **Outcome:** Success
- **Reflection:** *The agent provided a clear and concise explanation of how the production bug was handled, detailing the specific actions taken (increasing database connection pool size and adding retry logic). The agent also offered further assistance, indicating a proactive approach to user support.*
- **Importance Score:** 0.7
- **Trajectory Snapshot:** ['How did we handle the production bug yesterday?', 'Yesterday, we handled the production bug by increasing the database connection pool size and addi...

### Episode 5: What is my preferred tech stack and UI theme?
- **Outcome:** Success
- **Reflection:** *The agent successfully retrieved and communicated the user's preferred tech stack and UI theme accurately. The interaction was straightforward and the agent provided a clear and concise response, demonstrating an understanding of the user's preferences.*
- **Importance Score:** 0.7
- **Trajectory Snapshot:** ['What is my preferred tech stack and UI theme?', 'Your preferred tech stack includes Python for backend development and React for frontend developmen...


## 3. Semantic Memory (RAG Knowledge)
> **Nơi lưu:** ChromaDB. Dùng để lưu trữ kiến thức chuyên môn hoặc tài liệu thực tế.

- **Content:** Cách mạng Pháp (1789–1799) có nguyên nhân sâu xa từ sự bất bình đẳng trong xã hội phong kiến, khủng hoảng tài chính do nợ công và sự truyền bá tư tưởng Khai sáng. Sự kiện phá ngục Bastille là biểu tượ...
  - **Source:** Lịch sử thế giới
- **Content:** Python là ngôn ngữ phổ biến nhất cho Backend nhờ sự mạnh mẽ của Django và FastAPI. React là thư viện JavaScript hàng đầu cho Frontend, nổi tiếng với kiến trúc component và virtual DOM. Dark Mode không...
  - **Source:** Lập trình & Công nghệ

## 4. Short-term Memory (Current Context)
> **Nơi lưu:** Python List (Buffer). Giúp Agent hiểu ngữ cảnh của vài câu chat gần nhất.

Agent đang duy trì phiên chat với User ID: `test_user_999`.
Cơ chế: Sliding window (Tự động cắt tỉa khi vượt quá giới hạn Token).
