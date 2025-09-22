#!/usr/bin/env python3
"""
Main application integrating Kitchen Game and Pomodoro Timer
This demonstrates Phase 3: Session recording and statistics API
"""

import threading
import time
from deliverManager import (
    KitchenObjectSO, RecipeSO, RecipeListSO, PlateKitchenObject,
    KitchenGameManager, DeliveryManager
)
from pomodoro_session import get_pomodoro_timer, get_pomodoro_db
from pomodoro_api import app


def run_kitchen_game_with_pomodoro():
    """Run kitchen game with integrated Pomodoro timer"""
    print("🍅🍳 Kitchen Game with Pomodoro Timer")
    print("=" * 50)
    
    # Initialize Pomodoro system
    pomodoro_timer = get_pomodoro_timer()
    pomodoro_db = get_pomodoro_db()
    
    # Initialize kitchen game
    tomato = KitchenObjectSO("Tomato", 1)
    lettuce = KitchenObjectSO("Lettuce", 2)
    bread = KitchenObjectSO("Bread", 3)
    
    sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
    salad_recipe = RecipeSO("Salad", [lettuce, tomato])
    recipe_list = RecipeListSO([sandwich_recipe, salad_recipe])
    
    game_manager = KitchenGameManager.get_instance()
    game_manager.start_game()
    
    delivery_manager = DeliveryManager.get_instance(recipe_list)
    
    # Event handlers with Pomodoro integration
    def on_recipe_spawned(sender, args):
        print("📋 New recipe spawned!")
        # If we have an active pomodoro session, note the activity
        if pomodoro_timer.is_running:
            elapsed = pomodoro_timer.get_elapsed_time()
            print(f"   (During Pomodoro session - {elapsed:.1f}min elapsed)")
    
    def on_recipe_success(sender, args):
        print("✅ Recipe delivered successfully!")
        # Track successful deliveries during Pomodoro sessions
        if pomodoro_timer.is_running:
            remaining = pomodoro_timer.get_remaining_time()
            print(f"   (Great work! {remaining:.1f}min remaining in session)")
    
    def on_recipe_failed(sender, args):
        print("❌ Recipe delivery failed...")
        if pomodoro_timer.is_running:
            print("   (Stay focused! Try again during this Pomodoro session)")
    
    # Register event handlers
    delivery_manager.on_recipe_spawned.add_handler(on_recipe_spawned)
    delivery_manager.on_recipe_success.add_handler(on_recipe_success)
    delivery_manager.on_recipe_failed.add_handler(on_recipe_failed)
    
    print("\n🎮 Starting integrated game session...")
    
    # Start a Pomodoro session for focused cooking
    session = pomodoro_timer.start_session(
        duration_minutes=2,  # Short demo session
        task_description="Focused cooking session"
    )
    print(f"🍅 Started Pomodoro session: {session.task_description}")
    print(f"   Duration: {session.duration_minutes} minutes\n")
    
    # Game loop
    start_time = time.time()
    last_status_time = time.time()
    
    while time.time() - start_time < 30:  # Run for 30 seconds
        # Update delivery manager
        delivery_manager.update()
        
        # Check if Pomodoro session completed
        if pomodoro_timer.is_running and pomodoro_timer.is_session_complete():
            completed = pomodoro_timer.complete_session()
            print(f"\n🎉 Pomodoro session completed! Session ID: {completed.id}")
            print("💾 Session saved to database")
            
        # Show status every 5 seconds
        current_time = time.time()
        if current_time - last_status_time >= 5:
            waiting_recipes = len(delivery_manager.get_waiting_recipe_so_list())
            successful_recipes = delivery_manager.get_successful_recipes_amount()
            
            print(f"\n📊 Status Update:")
            print(f"   Waiting recipes: {waiting_recipes}")
            print(f"   Successful deliveries: {successful_recipes}")
            
            if pomodoro_timer.is_running:
                elapsed = pomodoro_timer.get_elapsed_time()
                remaining = pomodoro_timer.get_remaining_time()
                print(f"   🍅 Pomodoro: {elapsed:.1f}min elapsed, {remaining:.1f}min remaining")
            
            last_status_time = current_time
        
        time.sleep(0.1)
    
    # Simulate some recipe deliveries
    print("\n🚚 Simulating recipe deliveries...")
    
    # Deliver a sandwich
    plate = PlateKitchenObject()
    plate.add_kitchen_object(bread)
    plate.add_kitchen_object(lettuce)
    plate.add_kitchen_object(tomato)
    delivery_manager.deliver_recipe(plate)
    
    # Complete Pomodoro if still running
    if pomodoro_timer.is_running:
        completed = pomodoro_timer.complete_session()
        print(f"\n✅ Manually completed Pomodoro session ID: {completed.id}")
    
    # Show final statistics
    print("\n📈 Final Session Statistics:")
    print(f"   Total recipe deliveries: {delivery_manager.get_successful_recipes_amount()}")
    
    stats = pomodoro_db.get_today_stats()
    print(f"   Today's Pomodoro sessions: {stats['completed_sessions']}")
    print(f"   Total focus time today: {stats['total_minutes']} minutes")
    
    return stats


def run_api_server():
    """Run the Flask API server in a separate thread"""
    print("🌐 Starting API server on http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)


def main():
    """Main application entry point"""
    print("🚀 Phase 3: Pomodoro Session Recording & Statistics")
    print("Integrating Kitchen Game with Pomodoro Timer and API")
    print("=" * 60)
    
    # Option 1: Run integrated demo
    print("\n1. Running integrated kitchen game with Pomodoro...")
    stats = run_kitchen_game_with_pomodoro()
    
    print("\n" + "=" * 60)
    print("🎯 Phase 3 Implementation Complete!")
    print("\nFeatures implemented:")
    print("✅ PomodoroSession model with database persistence")
    print("✅ Session completion tracking and DB storage")
    print("✅ /api/stats/today endpoint for statistics")
    print("✅ Complete REST API for session management")
    print("✅ Integration with existing kitchen game system")
    
    print(f"\n📊 Today's Statistics Summary:")
    print(f"   Sessions completed: {stats['completed_sessions']}")
    print(f"   Total focus time: {stats['total_minutes']} minutes")
    print(f"   Sessions recorded: {len(stats['sessions'])}")
    
    # Option 2: Run API server
    print("\n" + "=" * 60)
    print("🌐 To start the API server, run:")
    print("   python3 pomodoro_api.py")
    print("\n📋 To run comprehensive tests:")
    print("   # Start API server first, then run:")
    print("   python3 test_pomodoro_api.py")


if __name__ == "__main__":
    main()