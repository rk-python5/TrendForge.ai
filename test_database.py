"""
Test script to verify database setup
Run this to make sure everything is working!
"""

from storage.database import db
from config.settings import settings
from rich.console import Console
from rich.table import Table

console = Console()


def test_database():
    """Test database operations"""
    
    console.print("\n[bold cyan]🧪 Testing Database Setup...[/bold cyan]\n")
    
    # 1. Create tables
    console.print("[yellow]1. Creating database tables...[/yellow]")
    db.create_tables()
    
    # 2. Test creating a post
    console.print("[yellow]2. Creating a test post...[/yellow]")
    test_post = db.create_post(
        topic="AI in 2024",
        content="AI is transforming how we work. Here are 3 key trends I'm watching:\n\n1. Agentic AI\n2. Multimodal models\n3. Local LLMs\n\nWhat trends are you excited about?",
        post_type="insight",
        tone="professional",
        hashtags="#AI #Technology #Innovation"
    )
    console.print(f"   ✅ Created post with ID: {test_post.id}")
    
    # 3. Retrieve the post
    console.print("[yellow]3. Retrieving the post...[/yellow]")
    retrieved_post = db.get_post(test_post.id)
    console.print(f"   ✅ Retrieved: {retrieved_post.topic}")
    
    # 4. Update post status
    console.print("[yellow]4. Updating post status to 'approved'...[/yellow]")
    post_id = test_post.id  # Use post_id for clarity
    db.update_post(post_id, {"status": "approved"})
    updated_post = db.get_post(post_id)  # Fetch fresh from DB
    console.print(f"   ✅ Status updated: {updated_post.status}")
    
    # 5. Add analytics
    console.print("[yellow]5. Adding analytics data...[/yellow]")
    analytics = db.add_analytics(
        post_id=test_post.id,
        likes=150,
        comments=23,
        shares=12,
        impressions=5000,
        notes="Great engagement on this post!"
    )
    console.print(f"   ✅ Analytics added: {analytics.engagement_rate:.2f}% engagement rate")
    
    # 6. Create a template
    console.print("[yellow]6. Creating a post template...[/yellow]")
    template = db.create_template(
        name="Success Story Template",
        category="story",
        template_text="Today I want to share a story about {topic}.\n\nThe challenge: {challenge}\n\nWhat I learned: {lesson}\n\nKey takeaway: {takeaway}",
        description="Template for sharing success stories and lessons learned"
    )
    console.print(f"   ✅ Template created: {template.name}")
    
    # 7. Add content idea
    console.print("[yellow]7. Adding a content idea...[/yellow]")
    idea = db.add_content_idea(
        idea="Write about the impact of AI agents on productivity",
        category="insight",
        priority="high"
    )
    console.print(f"   ✅ Content idea added (ID: {idea.id})")
    
    # 8. Get statistics
    console.print("[yellow]8. Fetching database statistics...[/yellow]")
    stats = db.get_stats()
    
    # Display stats in a table
    table = Table(title="\n📊 Database Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="green")
    
    for key, value in stats.items():
        table.add_row(key.replace("_", " ").title(), str(value))
    
    console.print(table)
    
    # 9. Show settings
    console.print("\n[yellow]9. Current Settings:[/yellow]")
    console.print(f"   User: {settings.user_name}")
    console.print(f"   Industry: {settings.user_industry}")
    console.print(f"   Expertise: {settings.user_expertise}")
    console.print(f"   Default Tone: {settings.tone}")
    console.print(f"   Ollama Model: {settings.ollama_model}")
    
    console.print("\n[bold green]✅ All database tests passed![/bold green]")
    console.print("\n[dim]Check the 'data/agent.db' file - your database is ready![/dim]\n")


if __name__ == "__main__":
    test_database()
