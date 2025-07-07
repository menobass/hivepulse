"""
User Manager Module
Handles user and business management for the Hive Ecuador Pulse bot
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from database.manager import DatabaseManager
from utils.helpers import validate_username


class UserManager:
    """Manages users and businesses for the analytics bot"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize user manager with database manager"""
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def add_user(self, username: str, requester: Optional[str] = None) -> Tuple[bool, str]:
        """Add a user to tracking"""
        self.logger.info(f"Adding user {username} to tracking (requested by {requester})")
        
        try:
            # Validate username
            if not validate_username(username):
                return False, "❌ Nombre de usuario inválido. Debe tener 3-16 caracteres, solo letras, números, puntos y guiones."
            
            # Check if user already exists
            tracked_users = self.db_manager.get_tracked_users()
            if username in tracked_users:
                return False, f"ℹ️ El usuario @{username} ya está siendo tracked."
            
            # Add user to database
            success = self.db_manager.add_user(username)
            
            if success:
                message = f"✅ Usuario @{username} agregado exitosamente al tracking."
                self.logger.info(f"User {username} added successfully")
                return True, message
            else:
                message = f"❌ Error al agregar el usuario @{username}."
                return False, message
                
        except Exception as e:
            self.logger.error(f"Error adding user {username}: {str(e)}")
            return False, "❌ Error interno al agregar el usuario."
    
    def remove_user(self, username: str, requester: Optional[str] = None) -> Tuple[bool, str]:
        """Remove a user from tracking"""
        self.logger.info(f"Removing user {username} from tracking (requested by {requester})")
        
        try:
            # Check if user exists
            tracked_users = self.db_manager.get_tracked_users()
            if username not in tracked_users:
                return False, f"ℹ️ El usuario @{username} no está siendo tracked."
            
            # Remove user from database
            success = self.db_manager.remove_user(username)
            
            if success:
                message = f"✅ Usuario @{username} removido exitosamente del tracking."
                self.logger.info(f"User {username} removed successfully")
                return True, message
            else:
                message = f"❌ Error al remover el usuario @{username}."
                return False, message
                
        except Exception as e:
            self.logger.error(f"Error removing user {username}: {str(e)}")
            return False, "❌ Error interno al remover el usuario."
    
    def add_business(self, username: str, business_name: str, category: str = "General", 
                    description: str = "", requester: Optional[str] = None) -> Tuple[bool, str]:
        """Add a business to tracking"""
        self.logger.info(f"Adding business {business_name} ({username}) to tracking (requested by {requester})")
        
        try:
            # Validate username
            if not validate_username(username):
                return False, "❌ Nombre de usuario inválido."
            
            # Validate business name
            if not business_name or len(business_name.strip()) < 3:
                return False, "❌ El nombre del negocio debe tener al menos 3 caracteres."
            
            # Check if business already exists
            businesses = self.db_manager.get_registered_businesses()
            existing_business = next((b for b in businesses if b['username'] == username), None)
            
            if existing_business:
                return False, f"ℹ️ El usuario @{username} ya tiene un negocio registrado: {existing_business['business_name']}"
            
            # Add business to database
            success = self.db_manager.add_business(username, business_name, category, description)
            
            if success:
                message = f"✅ Negocio '{business_name}' (@{username}) agregado exitosamente."
                self.logger.info(f"Business {business_name} added successfully")
                return True, message
            else:
                message = f"❌ Error al agregar el negocio '{business_name}'."
                return False, message
                
        except Exception as e:
            self.logger.error(f"Error adding business {business_name}: {str(e)}")
            return False, "❌ Error interno al agregar el negocio."
    
    def remove_business(self, username: str, requester: Optional[str] = None) -> Tuple[bool, str]:
        """Remove a business from tracking"""
        self.logger.info(f"Removing business for {username} (requested by {requester})")
        
        try:
            # Check if business exists
            businesses = self.db_manager.get_registered_businesses()
            business = next((b for b in businesses if b['username'] == username), None)
            
            if not business:
                return False, f"ℹ️ El usuario @{username} no tiene un negocio registrado."
            
            # Remove business from database
            success = self.db_manager.remove_business(username)
            
            if success:
                message = f"✅ Negocio '{business['business_name']}' (@{username}) removido exitosamente."
                self.logger.info(f"Business for {username} removed successfully")
                return True, message
            else:
                message = f"❌ Error al remover el negocio de @{username}."
                return False, message
                
        except Exception as e:
            self.logger.error(f"Error removing business for {username}: {str(e)}")
            return False, "❌ Error interno al remover el negocio."
    
    def list_tracked_users(self, limit: int = 50) -> Tuple[bool, str]:
        """List all tracked users"""
        self.logger.info("Listing tracked users")
        
        try:
            users = self.db_manager.get_tracked_users()
            
            if not users:
                return True, "ℹ️ No hay usuarios siendo tracked actualmente."
            
            # Limit the number of users shown
            users_to_show = users[:limit]
            
            message = f"📋 **Usuarios Tracked ({len(users)} total):**\n\n"
            
            # Group users by first letter for better organization
            users_by_letter = {}
            for user in users_to_show:
                first_letter = user[0].upper()
                if first_letter not in users_by_letter:
                    users_by_letter[first_letter] = []
                users_by_letter[first_letter].append(user)
            
            # Format output
            for letter in sorted(users_by_letter.keys()):
                message += f"**{letter}:** "
                message += ", ".join([f"@{user}" for user in users_by_letter[letter]])
                message += "\n"
            
            if len(users) > limit:
                message += f"\n*... y {len(users) - limit} usuarios más*"
            
            return True, message
            
        except Exception as e:
            self.logger.error(f"Error listing tracked users: {str(e)}")
            return False, "❌ Error al obtener la lista de usuarios."
    
    def list_businesses(self, limit: int = 20) -> Tuple[bool, str]:
        """List all registered businesses"""
        self.logger.info("Listing registered businesses")
        
        try:
            businesses = self.db_manager.get_registered_businesses()
            
            if not businesses:
                return True, "ℹ️ No hay negocios registrados actualmente."
            
            # Limit the number of businesses shown
            businesses_to_show = businesses[:limit]
            
            message = f"🏢 **Negocios Registrados ({len(businesses)} total):**\n\n"
            
            # Group businesses by category
            businesses_by_category = {}
            for business in businesses_to_show:
                category = business.get('category', 'General')
                if category not in businesses_by_category:
                    businesses_by_category[category] = []
                businesses_by_category[category].append(business)
            
            # Format output
            for category in sorted(businesses_by_category.keys()):
                message += f"**{category}:**\n"
                for business in businesses_by_category[category]:
                    name = business['business_name']
                    username = business['username']
                    added_date = business.get('added_date', 'N/A')
                    message += f"- 🏪 **{name}** (@{username}) - *Registrado: {added_date}*\n"
                message += "\n"
            
            if len(businesses) > limit:
                message += f"*... y {len(businesses) - limit} negocios más*"
            
            return True, message
            
        except Exception as e:
            self.logger.error(f"Error listing businesses: {str(e)}")
            return False, "❌ Error al obtener la lista de negocios."
    
    def get_user_stats(self, username: str, days: int = 30) -> Tuple[bool, str]:
        """Get statistics for a specific user"""
        self.logger.info(f"Getting stats for user {username}")
        
        try:
            # Check if user is tracked
            tracked_users = self.db_manager.get_tracked_users()
            if username not in tracked_users:
                return False, f"ℹ️ El usuario @{username} no está siendo tracked."
            
            # Get user activity history
            activity_history = self.db_manager.get_user_activity_history(username, days)
            
            if not activity_history:
                return True, f"ℹ️ No hay datos de actividad para @{username} en los últimos {days} días."
            
            # Calculate statistics
            total_posts = sum(activity['posts_count'] for activity in activity_history)
            total_comments = sum(activity['comments_count'] for activity in activity_history)
            total_upvotes_given = sum(activity['upvotes_given'] for activity in activity_history)
            total_upvotes_received = sum(activity['upvotes_received'] for activity in activity_history)
            
            avg_engagement = sum(activity['engagement_score'] for activity in activity_history) / len(activity_history)
            active_days = len(activity_history)
            
            # Find best day
            best_day = max(activity_history, key=lambda x: x['engagement_score'])
            
            message = f"📊 **Estadísticas de @{username}** (últimos {days} días):\n\n"
            message += f"🗓️ **Días activos:** {active_days}\n"
            message += f"📝 **Posts totales:** {total_posts}\n"
            message += f"💬 **Comentarios totales:** {total_comments}\n"
            message += f"👍 **Upvotes dados:** {total_upvotes_given}\n"
            message += f"⭐ **Upvotes recibidos:** {total_upvotes_received}\n"
            message += f"🎯 **Engagement promedio:** {avg_engagement:.1f}\n"
            message += f"🏆 **Mejor día:** {best_day['date']} (engagement: {best_day['engagement_score']:.1f})\n"
            
            # Activity level
            if avg_engagement >= 50:
                activity_level = "🔥 Muy Alto"
            elif avg_engagement >= 30:
                activity_level = "💪 Alto"
            elif avg_engagement >= 15:
                activity_level = "👍 Medio"
            elif avg_engagement >= 5:
                activity_level = "👌 Bajo"
            else:
                activity_level = "😴 Muy Bajo"
            
            message += f"📈 **Nivel de actividad:** {activity_level}\n"
            
            return True, message
            
        except Exception as e:
            self.logger.error(f"Error getting user stats for {username}: {str(e)}")
            return False, "❌ Error al obtener las estadísticas del usuario."
    
    def get_business_stats(self, username: str, days: int = 30) -> Tuple[bool, str]:
        """Get statistics for a specific business"""
        self.logger.info(f"Getting business stats for {username}")
        
        try:
            # Check if business exists
            businesses = self.db_manager.get_registered_businesses()
            business = next((b for b in businesses if b['username'] == username), None)
            
            if not business:
                return False, f"ℹ️ El usuario @{username} no tiene un negocio registrado."
            
            # Get transaction history
            transactions = self.db_manager.get_business_transaction_history(username, days)
            
            if not transactions:
                return True, f"ℹ️ No hay transacciones registradas para el negocio de @{username} en los últimos {days} días."
            
            # Calculate statistics
            total_transactions = len(transactions)
            total_volume = sum(float(tx['amount']) for tx in transactions)
            avg_transaction = total_volume / total_transactions if total_transactions > 0 else 0
            
            # Transaction categories
            incoming = [tx for tx in transactions if tx['to_user'] == username]
            outgoing = [tx for tx in transactions if tx['from_user'] == username]
            
            incoming_volume = sum(float(tx['amount']) for tx in incoming)
            outgoing_volume = sum(float(tx['amount']) for tx in outgoing)
            
            # Find largest transaction
            largest_tx = max(transactions, key=lambda x: float(x['amount']))
            
            message = f"💼 **Estadísticas del Negocio '{business['business_name']}'** (@{username}):\n\n"
            message += f"🏪 **Categoría:** {business.get('category', 'General')}\n"
            message += f"📅 **Registrado:** {business.get('added_date', 'N/A')}\n\n"
            
            message += f"📊 **Actividad (últimos {days} días):**\n"
            message += f"💰 **Transacciones totales:** {total_transactions}\n"
            message += f"💵 **Volumen total:** ${total_volume:.3f} HBD\n"
            message += f"📈 **Transacción promedio:** ${avg_transaction:.3f} HBD\n"
            message += f"📥 **Recibido:** ${incoming_volume:.3f} HBD ({len(incoming)} transacciones)\n"
            message += f"📤 **Enviado:** ${outgoing_volume:.3f} HBD ({len(outgoing)} transacciones)\n"
            message += f"🏆 **Transacción más grande:** ${float(largest_tx['amount']):.3f} HBD\n"
            
            # Activity level
            if total_volume >= 100:
                activity_level = "🔥 Muy Alto"
            elif total_volume >= 50:
                activity_level = "💪 Alto"
            elif total_volume >= 20:
                activity_level = "👍 Medio"
            elif total_volume >= 5:
                activity_level = "👌 Bajo"
            else:
                activity_level = "😴 Muy Bajo"
            
            message += f"📊 **Nivel de actividad:** {activity_level}\n"
            
            return True, message
            
        except Exception as e:
            self.logger.error(f"Error getting business stats for {username}: {str(e)}")
            return False, "❌ Error al obtener las estadísticas del negocio."
    
    def get_community_summary(self) -> Tuple[bool, str]:
        """Get a summary of the community"""
        self.logger.info("Getting community summary")
        
        try:
            # Get counts
            tracked_users = self.db_manager.get_tracked_users()
            businesses = self.db_manager.get_registered_businesses()
            
            user_count = len(tracked_users)
            business_count = len(businesses)
            
            # Get recent activity
            community_trends = self.db_manager.get_community_trends(7)
            
            message = f"🇪🇨 **Resumen de Hive Ecuador Pulse:**\n\n"
            message += f"👥 **Usuarios tracked:** {user_count}\n"
            message += f"🏢 **Negocios registrados:** {business_count}\n"
            
            if community_trends:
                latest_stats = community_trends[0]
                message += f"📊 **Última actividad registrada:**\n"
                message += f"- 📅 Fecha: {latest_stats['date']}\n"
                message += f"- 👥 Usuarios activos: {latest_stats['active_users']}\n"
                message += f"- 📝 Posts: {latest_stats['total_posts']}\n"
                message += f"- 💬 Comentarios: {latest_stats['total_comments']}\n"
                message += f"- 👍 Upvotes: {latest_stats['total_upvotes']}\n"
                message += f"- 🎯 Engagement: {latest_stats['engagement_rate']:.2f}\n"
                message += f"- 💪 Salud comunitaria: {latest_stats['health_index']:.1f}/100\n"
            
            # Business categories
            if businesses:
                categories = {}
                for business in businesses:
                    category = business.get('category', 'General')
                    categories[category] = categories.get(category, 0) + 1
                
                message += f"\n🏪 **Negocios por categoría:**\n"
                for category, count in sorted(categories.items()):
                    message += f"- {category}: {count} negocio{'s' if count > 1 else ''}\n"
            
            return True, message
            
        except Exception as e:
            self.logger.error(f"Error getting community summary: {str(e)}")
            return False, "❌ Error al obtener el resumen de la comunidad."
    
    def is_user_tracked(self, username: str) -> bool:
        """Check if a user is being tracked"""
        try:
            tracked_users = self.db_manager.get_tracked_users()
            return username in tracked_users
        except Exception as e:
            self.logger.error(f"Error checking if user is tracked: {str(e)}")
            return False
    
    def is_business_registered(self, username: str) -> bool:
        """Check if a user has a registered business"""
        try:
            businesses = self.db_manager.get_registered_businesses()
            return any(b['username'] == username for b in businesses)
        except Exception as e:
            self.logger.error(f"Error checking if business is registered: {str(e)}")
            return False
    
    def get_user_count(self) -> int:
        """Get total number of tracked users"""
        try:
            return len(self.db_manager.get_tracked_users())
        except Exception as e:
            self.logger.error(f"Error getting user count: {str(e)}")
            return 0
    
    def get_business_count(self) -> int:
        """Get total number of registered businesses"""
        try:
            return len(self.db_manager.get_registered_businesses())
        except Exception as e:
            self.logger.error(f"Error getting business count: {str(e)}")
            return 0
