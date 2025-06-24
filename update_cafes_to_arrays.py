#!/usr/bin/env python3
"""
Update existing cafes in the database to use array-based tag fields:
- atmosphere: now an array of 4-5 values
- energy_level: now an array of 4-5 values  
- study_friendly: now an array of 4-5 values
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import Database
from app.repositories.cafe_repository import CafeRepository

async def update_cafes_to_arrays():
    """Update all existing cafes to use array-based tag fields"""
    print("🔄 Connecting to database...")
    await Database.connect_db()
    
    print("📝 Converting cafe tag fields from single values to arrays...")
    print("   Each cafe will now have 4-5 tags per field:")
    print("   - atmosphere: 4-5 values from [Cozy, Rustic, Traditional, Warm, Clean]")
    print("   - energy_level: 4-5 values from [quiet, low-key, tranquil, moderate, average]")
    print("   - study_friendly: 4-5 values from [study heaven, good, decent, mixed, fair]")
    
    cafe_repo = CafeRepository()
    updated_count = await cafe_repo.update_all_cafes_with_array_fields()
    
    print(f"\n✅ Successfully updated {updated_count} cafes to use array-based tag fields!")
    print("   Each cafe now has rich, multi-dimensional tagging for better filtering and search.")
    
    await Database.close_db()
    print("🔒 Database connection closed")

if __name__ == "__main__":
    asyncio.run(update_cafes_to_arrays()) 