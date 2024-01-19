# SoulMateBot
Telebot "Soulmate" for English Language Assessment

Description:

Primary Objective: Developed a Telegram bot tailored for an English language school to assess students' proficiency in the language and discern their preferred learning style.

English Proficiency Test: The bot administers a series of questions to gauge the user's grasp on the English language. Based on the answers, it then determines the user's current English proficiency level.

Learning Style Assessment: Post the proficiency test, the bot evaluates the user's most effective learning style. This helps educators tailor teaching methods to better suit each student's needs.

Database Integration:

Utilized SQLAlchemy to handle database interactions seamlessly.
Integrated the bot with a PostgreSQL database where students' information, proficiency levels, and preferred learning styles are stored for further analysis by educators.
Implemented routines to check for the existence of required tables and set them up if absent.
Interactive User Experience: Leveraged inline keyboards and diverse conversation handlers, ensuring smooth user-bot interactions. Users can navigate the bot's functionalities using commands such as /start and /help.

Error Management: Designed the bot with strong error handling mechanisms to manage potential database issues or unexpected inputs, ensuring uninterrupted user experience.

Environment Configuration: Established a virtual environment to house the project's dependencies, guaranteeing consistency across setups.

Continuous Testing: Regular phases of testing and iterative development were undertaken to guarantee the bot's optimal performance and deliver an intuitive user experience.
