"""
Terminal UI for LinkedIn AI Agent
Interactive interface with human-in-the-loop approval
"""

from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.markdown import Markdown
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from graph.workflow import workflow
from storage.database import db
from agents.content_generator import content_agent
from utils.helpers import format_post_for_display, get_post_metrics
from config.settings import settings

console = Console()


class TerminalUI:
    """
    Interactive terminal interface for the LinkedIn AI Agent
    """
    
    def __init__(self):
        """Initialize the terminal UI"""
        self.workflow = workflow
        self.db = db
        self.agent = content_agent
        self.console = console
    
    def show_banner(self):
        """Display welcome banner"""
        banner = """
[bold cyan]╔══════════════════════════════════════════════════╗
║                                                  ║
║        LinkedIn AI Agent 🤖                      ║
║        Your Personal Content Generator           ║
║                                                  ║
╚══════════════════════════════════════════════════╝[/bold cyan]

[dim]Generate engaging LinkedIn posts with AI assistance[/dim]
"""
        self.console.print(banner)
    
    def show_menu(self) -> str:
        """Show main menu and get user choice"""
        menu = Table(show_header=False, box=None)
        menu.add_column(style="cyan", width=5)
        menu.add_column(style="white")
        
        menu.add_row("1.", "Generate a new post")
        menu.add_row("2.", "View saved posts")
        menu.add_row("3.", "View statistics")
        menu.add_row("4.", "Settings")
        menu.add_row("5.", "Exit")
        
        self.console.print("\n[bold]Main Menu:[/bold]")
        self.console.print(menu)
        
        choice = Prompt.ask("\nWhat would you like to do?", choices=["1", "2", "3", "4", "5"], default="1")
        return choice
    
    def generate_post_flow(self):
        """
        Main flow for generating a post with human approval
        """
        self.console.print("\n[bold cyan]🚀 Generate New Post[/bold cyan]\n")
        
        # Ask for input method
        input_method = Prompt.ask(
            "How would you like to start?",
            choices=["topic", "theme"],
            default="topic"
        )
        
        if input_method == "topic":
            topic = Prompt.ask("Enter your post topic")
            theme = None
        else:
            theme = Prompt.ask("Enter a general theme")
            topic = None
        
        # Ask for post type
        post_type = Prompt.ask(
            "Post type",
            choices=settings.POST_TYPES,
            default="insight"
        )
        
        # Ask for tone
        tone = Prompt.ask(
            "Tone",
            choices=settings.TONES,
            default=settings.tone
        )
        
        # Generate the post
        self.console.print("\n[yellow]Generating your post...[/yellow]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Working...", total=None)
            
            try:
                if topic:
                    result = self.workflow.run_with_topic(topic, post_type, tone)
                else:
                    result = self.workflow.run_with_theme(theme, post_type, tone)
                
                progress.update(task, completed=True)
                
            except Exception as e:
                self.console.print(f"\n[red]❌ Error: {e}[/red]\n")
                return
        
        # Check for errors
        if result.get("status") == "error":
            self.console.print(f"\n[red]❌ Error: {result.get('error', 'Unknown error')}[/red]\n")
            return
        
        # Debug: Check what we got
        if not result.get("content"):
            self.console.print(f"\n[red]❌ Error: No content in result. Status: {result.get('status')}[/red]")
            self.console.print(f"[dim]Result keys: {list(result.keys())}[/dim]\n")
            return
        
        # Show generated ideas if theme was used
        if result.get("post_ideas"):
            self._show_generated_ideas(result["post_ideas"], result["selected_idea"])
        
        # Show the generated post
        self._show_post(result)
        
        # Human approval loop
        approved = self._approval_loop(result)
        
        if approved:
            # Update status in database
            self.db.update_post_status(result["post_id"], "approved")
            self.console.print("\n[bold green]✅ Post approved and saved![/bold green]\n")
            
            # Ask if they want to export
            if Confirm.ask("Would you like to export this post?"):
                self._export_post(result["post_id"])
        else:
            # Delete the draft
            self.db.delete_post(result["post_id"])
            self.console.print("\n[yellow]Post discarded.[/yellow]\n")
    
    def _show_generated_ideas(self, ideas: List[str], selected: str):
        """Display generated post ideas"""
        ideas_table = Table(title="Generated Post Ideas", show_lines=True)
        ideas_table.add_column("#", style="cyan", width=5)
        ideas_table.add_column("Idea", style="white")
        ideas_table.add_column("Status", style="green", width=10)
        
        for i, idea in enumerate(ideas, 1):
            status = "✓ Selected" if idea == selected else ""
            style = "bold green" if idea == selected else "white"
            ideas_table.add_row(str(i), f"[{style}]{idea}[/{style}]", status)
        
        self.console.print(ideas_table)
        self.console.print()
    
    def _show_post(self, result: dict):
        """Display the generated post"""
        # Get content - it might be in different places depending on the workflow
        content = result.get("content", "")
        hashtags = result.get("hashtags", "")
        
        formatted_post = format_post_for_display(content, hashtags)
        
        # Show the post
        self.console.print(Panel(
            formatted_post,
            title="[bold green]Generated LinkedIn Post[/bold green]",
            border_style="green",
            padding=(1, 2)
        ))
        
        # Show metrics - safely handle the content
        if content:
            metrics = get_post_metrics(content)
            metrics_text = f"📊 {metrics['word_count']} words | {metrics['character_count']} characters | ~{metrics['reading_time_seconds']}s read time"
            
            if result.get("review_score"):
                metrics_text += f" | Quality: {result['review_score']}/10"
            
            self.console.print(f"\n[dim]{metrics_text}[/dim]\n")
        else:
            self.console.print(f"\n[red]Error: No content generated[/red]\n")
    
    def _approval_loop(self, result: dict) -> bool:
        """
        Human-in-the-loop approval process
        
        Returns:
            True if approved, False if rejected
        """
        while True:
            choice = Prompt.ask(
                "\nWhat would you like to do?",
                choices=["approve", "reject", "edit", "regenerate", "review"],
                default="approve"
            )
            
            if choice == "approve":
                return True
            
            elif choice == "reject":
                return False
            
            elif choice == "edit":
                edited_content = self._edit_post(result["content"])
                if edited_content:
                    result["content"] = edited_content
                    self.db.update_post_content(result["post_id"], edited_content)
                    self._show_post(result)
            
            elif choice == "regenerate":
                feedback = Prompt.ask("What should I improve? (optional)", default="")
                self.console.print("\n[yellow]Regenerating...[/yellow]\n")
                
                if feedback:
                    improved = self.agent.improve_post(
                        post_id=result["post_id"],
                        feedback=feedback,
                        save_as_new=False
                    )
                    result["content"] = improved["content"]
                else:
                    # Generate fresh version
                    new_result = self.agent.generate_post(
                        topic=result["topic"],
                        post_type=result["post_type"],
                        tone=result["tone"],
                        save_to_db=False
                    )
                    result["content"] = new_result["content"]
                    self.db.update_post_content(result["post_id"], new_result["content"])
                
                self._show_post(result)
            
            elif choice == "review":
                self._show_review(result["post_id"])
    
    def _edit_post(self, current_content: str) -> Optional[str]:
        """Allow user to edit post content"""
        self.console.print("\n[yellow]Opening editor... (Press ESC then ENTER to finish)[/yellow]\n")
        
        try:
            # Use prompt_toolkit for multi-line editing
            edited = prompt(
                "Edit your post:\n",
                default=current_content,
                multiline=True
            )
            return edited.strip()
        except (KeyboardInterrupt, EOFError):
            return None
    
    def _show_review(self, post_id: int):
        """Show detailed review of the post"""
        post = self.db.get_post(post_id)
        if not post:
            return
        
        review = self.agent.review_post(post.content)
        
        self.console.print(Panel(
            review["review"],
            title="[bold blue]Post Review[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        ))
    
    def _export_post(self, post_id: int):
        """Export post to markdown file"""
        post = self.db.get_post(post_id)
        if not post:
            return
        
        filename = f"post_{post.id}_{post.created_at.strftime('%Y%m%d_%H%M%S')}.md"
        
        content = format_post_for_display(post.content, post.hashtags)
        
        with open(filename, 'w') as f:
            f.write(f"# {post.topic}\n\n")
            f.write(f"**Type:** {post.post_type} | **Tone:** {post.tone}\n\n")
            f.write(f"---\n\n")
            f.write(content)
        
        self.console.print(f"\n[green]✅ Exported to: {filename}[/green]\n")
    
    def view_posts(self):
        """View all saved posts"""
        self.console.print("\n[bold cyan]📚 Saved Posts[/bold cyan]\n")
        
        posts = self.db.get_all_posts(limit=20)
        
        if not posts:
            self.console.print("[yellow]No posts yet. Create your first one![/yellow]\n")
            return
        
        table = Table(show_lines=True)
        table.add_column("ID", style="cyan", width=5)
        table.add_column("Topic", style="white", width=40)
        table.add_column("Type", style="green", width=10)
        table.add_column("Status", style="yellow", width=10)
        table.add_column("Created", style="dim", width=15)
        
        for post in posts:
            from utils.helpers import format_datetime, truncate_text
            table.add_row(
                str(post.id),
                truncate_text(post.topic, 40),
                post.post_type,
                post.status,
                format_datetime(post.created_at)
            )
        
        self.console.print(table)
        self.console.print()
        
        # Ask if they want to view details
        if Confirm.ask("View a specific post?"):
            post_id = int(Prompt.ask("Enter post ID"))
            self._view_post_details(post_id)
    
    def _view_post_details(self, post_id: int):
        """View detailed post information"""
        post = self.db.get_post(post_id)
        
        if not post:
            self.console.print("[red]Post not found[/red]\n")
            return
        
        formatted = format_post_for_display(post.content, post.hashtags)
        
        self.console.print(Panel(
            formatted,
            title=f"[bold]Post #{post.id}: {post.topic}[/bold]",
            subtitle=f"Status: {post.status} | Type: {post.post_type} | Tone: {post.tone}",
            border_style="blue",
            padding=(1, 2)
        ))
    
    def show_stats(self):
        """Display statistics"""
        self.console.print("\n[bold cyan]📊 Statistics[/bold cyan]\n")
        
        stats = self.db.get_stats()
        
        table = Table(title="Overall Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green", justify="right")
        
        for key, value in stats.items():
            table.add_row(key.replace("_", " ").title(), str(value))
        
        self.console.print(table)
        self.console.print()
    
    def show_settings(self):
        """Show current settings"""
        self.console.print("\n[bold cyan]⚙️  Settings[/bold cyan]\n")
        
        table = Table()
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("User Name", settings.user_name)
        table.add_row("Industry", settings.user_industry)
        table.add_row("Expertise", settings.user_expertise)
        table.add_row("Default Tone", settings.tone)
        table.add_row("Ollama Model", settings.ollama_model)
        
        self.console.print(table)
        self.console.print("\n[dim]Edit .env file to change settings[/dim]\n")
    
    def run(self):
        """Main run loop"""
        self.show_banner()
        
        while True:
            try:
                choice = self.show_menu()
                
                if choice == "1":
                    self.generate_post_flow()
                elif choice == "2":
                    self.view_posts()
                elif choice == "3":
                    self.show_stats()
                elif choice == "4":
                    self.show_settings()
                elif choice == "5":
                    self.console.print("\n[bold cyan]👋 Goodbye![/bold cyan]\n")
                    break
                
            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Interrupted. Use option 5 to exit properly.[/yellow]\n")
                continue
            except Exception as e:
                self.console.print(f"\n[red]Error: {e}[/red]\n")
                continue


def main():
    """Main entry point"""
    ui = TerminalUI()
    ui.run()


if __name__ == "__main__":
    main()