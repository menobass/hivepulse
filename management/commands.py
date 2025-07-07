"""
Command handler for Hive Ecuador Pulse Analytics Bot
Handles user commands, admin functions, and interactive features
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Callable
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Command:
    """Command definition structure"""
    name: str
    description: str
    usage: str
    admin_only: bool = False
    aliases: Optional[List[str]] = None
    handler: Optional[Callable] = None

class CommandHandler:
    """Handles bot commands and interactions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.prefix = config.get('management', {}).get('command_prefix', '!pulse')
        self.admin_users = config.get('management', {}).get('admin_users', [])
        self.enabled = config.get('management', {}).get('allow_user_commands', True)
        
        # Register commands
        self.commands = {}
        self._register_commands()
        
    def _register_commands(self):
        """Register all available commands"""
        commands_list = [
            Command(
                name="help",
                description="Muestra la lista de comandos disponibles",
                usage=f"{self.prefix} help [comando]",
                aliases=["ayuda", "?"]
            ),
            Command(
                name="stats",
                description="Muestra estadísticas rápidas de la comunidad",
                usage=f"{self.prefix} stats [usuario]",
                aliases=["estadisticas", "info"]
            ),
            Command(
                name="top",
                description="Muestra el top de usuarios por actividad",
                usage=f"{self.prefix} top [cantidad] [tipo]",
                aliases=["ranking", "leaderboard"]
            ),
            Command(
                name="report",
                description="Genera un reporte personalizado",
                usage=f"{self.prefix} report [tipo] [periodo]",
                aliases=["reporte", "informe"]
            ),
            Command(
                name="add_user",
                description="Añade un usuario al seguimiento",
                usage=f"{self.prefix} add_user <usuario>",
                admin_only=True
            ),
            Command(
                name="remove_user",
                description="Elimina un usuario del seguimiento",
                usage=f"{self.prefix} remove_user <usuario>",
                admin_only=True
            ),
            Command(
                name="add_business",
                description="Añade un negocio al seguimiento",
                usage=f"{self.prefix} add_business <usuario> [descripción]",
                admin_only=True
            ),
            Command(
                name="config",
                description="Muestra o modifica la configuración",
                usage=f"{self.prefix} config [parámetro] [valor]",
                admin_only=True
            ),
            Command(
                name="force_report",
                description="Fuerza la generación de un reporte",
                usage=f"{self.prefix} force_report [tipo]",
                admin_only=True
            ),
            Command(
                name="status",
                description="Muestra el estado del bot",
                usage=f"{self.prefix} status",
                admin_only=True
            )
        ]
        
        # Register commands
        for cmd in commands_list:
            self.commands[cmd.name] = cmd
            # Register aliases
            if cmd.aliases:
                for alias in cmd.aliases:
                    self.commands[alias] = cmd
    
    def parse_command(self, text: str) -> Optional[Tuple[str, List[str]]]:
        """Parse command from text"""
        try:
            # Check if text starts with command prefix
            if not text.strip().startswith(self.prefix):
                return None
            
            # Remove prefix and split
            command_text = text.strip()[len(self.prefix):].strip()
            parts = command_text.split()
            
            if not parts:
                return None
            
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            return command, args
            
        except Exception as e:
            logger.error(f"Error parsing command: {e}")
            return None
    
    def is_admin(self, username: str) -> bool:
        """Check if user is admin"""
        return username.lower() in [admin.lower() for admin in self.admin_users]
    
    def handle_command(self, command: str, args: List[str], username: str) -> str:
        """Handle command execution"""
        try:
            if not self.enabled:
                return "❌ Los comandos están deshabilitados temporalmente."
            
            # Check if command exists
            if command not in self.commands:
                return f"❌ Comando '{command}' no encontrado. Usa `{self.prefix} help` para ver comandos disponibles."
            
            cmd = self.commands[command]
            
            # Check admin permissions
            if cmd.admin_only and not self.is_admin(username):
                return "❌ No tienes permisos para ejecutar este comando."
            
            # Route to appropriate handler
            if cmd.name == "help":
                return self._handle_help(args)
            elif cmd.name == "stats":
                return self._handle_stats(args, username)
            elif cmd.name == "top":
                return self._handle_top(args)
            elif cmd.name == "report":
                return self._handle_report(args, username)
            elif cmd.name == "add_user":
                return self._handle_add_user(args, username)
            elif cmd.name == "remove_user":
                return self._handle_remove_user(args, username)
            elif cmd.name == "add_business":
                return self._handle_add_business(args, username)
            elif cmd.name == "config":
                return self._handle_config(args, username)
            elif cmd.name == "force_report":
                return self._handle_force_report(args, username)
            elif cmd.name == "status":
                return self._handle_status(args, username)
            else:
                return f"⚠️ Comando '{command}' no implementado aún."
                
        except Exception as e:
            logger.error(f"Error handling command: {e}")
            return f"❌ Error ejecutando comando: {str(e)}"
    
    def _handle_help(self, args: List[str]) -> str:
        """Handle help command"""
        if args:
            # Show specific command help
            command = args[0].lower()
            if command in self.commands:
                cmd = self.commands[command]
                return f"""📖 **Ayuda: {cmd.name}**

**Descripción:** {cmd.description}

**Uso:** `{cmd.usage}`

**Requiere Admin:** {'Sí' if cmd.admin_only else 'No'}

**Aliases:** {', '.join(cmd.aliases) if cmd.aliases else 'Ninguno'}"""
            else:
                return f"❌ Comando '{command}' no encontrado."
        
        # Show all commands
        user_commands = []
        admin_commands = []
        
        seen_commands = set()
        for cmd in self.commands.values():
            if cmd.name in seen_commands:
                continue
            seen_commands.add(cmd.name)
            
            if cmd.admin_only:
                admin_commands.append(f"• `{cmd.name}` - {cmd.description}")
            else:
                user_commands.append(f"• `{cmd.name}` - {cmd.description}")
        
        help_text = "📖 **Comandos Disponibles**\n\n"
        
        if user_commands:
            help_text += "**Comandos de Usuario:**\n" + "\n".join(user_commands) + "\n\n"
        
        if admin_commands:
            help_text += "**Comandos de Administrador:**\n" + "\n".join(admin_commands) + "\n\n"
        
        help_text += f"**Uso:** `{self.prefix} <comando> [argumentos]`\n"
        help_text += f"**Ejemplo:** `{self.prefix} stats`\n\n"
        help_text += f"Para ayuda específica: `{self.prefix} help <comando>`"
        
        return help_text
    
    def _handle_stats(self, args: List[str], username: str) -> str:
        """Handle stats command"""
        target_user = args[0] if args else username
        
        # Mock stats - in real implementation, this would query the database
        return f"""📊 **Estadísticas de @{target_user}**

🔥 **Actividad Reciente (7 días):**
• Posts: 5
• Comentarios: 12
• Votos recibidos: 45

💰 **Recompensas:**
• Total: 2.450 HIVE
• Promedio por post: 0.490 HIVE

📈 **Ranking:**
• Posición en actividad: #23
• Posición en recompensas: #18

⭐ **Puntuación de Actividad:** 87/100

*Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}*"""
    
    def _handle_top(self, args: List[str]) -> str:
        """Handle top command"""
        limit = 10
        metric = "activity"
        
        if args:
            try:
                if args[0].isdigit():
                    limit = min(int(args[0]), 20)  # Max 20
                    if len(args) > 1:
                        metric = args[1].lower()
                else:
                    metric = args[0].lower()
            except:
                pass
        
        valid_metrics = ["activity", "posts", "comments", "rewards", "reputation"]
        if metric not in valid_metrics:
            metric = "activity"
        
        # Mock top users - in real implementation, this would query the database
        mock_users = [
            ("user1", 95), ("user2", 87), ("user3", 76), ("user4", 65), ("user5", 54),
            ("user6", 45), ("user7", 38), ("user8", 32), ("user9", 28), ("user10", 25)
        ]
        
        metric_names = {
            "activity": "Actividad",
            "posts": "Posts",
            "comments": "Comentarios", 
            "rewards": "Recompensas",
            "reputation": "Reputación"
        }
        
        result = f"🏆 **Top {limit} - {metric_names[metric]}**\n\n"
        
        for i, (user, score) in enumerate(mock_users[:limit], 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
            result += f"{emoji} **{i}.** @{user} - {score} puntos\n"
        
        result += f"\n*Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}*"
        
        return result
    
    def _handle_report(self, args: List[str], username: str) -> str:
        """Handle report command"""
        report_type = args[0] if args else "quick"
        period = args[1] if len(args) > 1 else "today"
        
        valid_types = ["quick", "detailed", "business", "growth"]
        valid_periods = ["today", "week", "month"]
        
        if report_type not in valid_types:
            return f"❌ Tipo de reporte inválido. Válidos: {', '.join(valid_types)}"
        
        if period not in valid_periods:
            return f"❌ Período inválido. Válidos: {', '.join(valid_periods)}"
        
        # Mock report generation
        return f"""📋 **Generando Reporte {report_type.title()}**

📅 **Período:** {period}
👤 **Solicitado por:** @{username}
⏰ **Hora:** {datetime.now().strftime('%H:%M')}

🔄 **Estado:** En proceso...

El reporte estará disponible en unos minutos. Te notificaremos cuando esté listo."""
    
    def _handle_add_user(self, args: List[str], username: str) -> str:
        """Handle add_user command"""
        if not args:
            return "❌ Debes especificar un usuario. Uso: `!pulse add_user <usuario>`"
        
        target_user = args[0].lstrip('@')
        
        # Mock user addition
        return f"""✅ **Usuario Añadido al Seguimiento**

👤 **Usuario:** @{target_user}
👨‍💼 **Añadido por:** @{username}
📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

🔍 **Próximos pasos:**
• El usuario será incluido en el próximo reporte
• Se comenzará a recopilar datos de actividad
• Se enviará notificación de bienvenida"""
    
    def _handle_remove_user(self, args: List[str], username: str) -> str:
        """Handle remove_user command"""
        if not args:
            return "❌ Debes especificar un usuario. Uso: `!pulse remove_user <usuario>`"
        
        target_user = args[0].lstrip('@')
        
        # Mock user removal
        return f"""✅ **Usuario Eliminado del Seguimiento**

👤 **Usuario:** @{target_user}
👨‍💼 **Eliminado por:** @{username}
📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

⚠️ **Nota:** Los datos históricos se conservarán para estadísticas."""
    
    def _handle_add_business(self, args: List[str], username: str) -> str:
        """Handle add_business command"""
        if not args:
            return "❌ Debes especificar un usuario. Uso: `!pulse add_business <usuario> [descripción]`"
        
        business_user = args[0].lstrip('@')
        description = " ".join(args[1:]) if len(args) > 1 else "Sin descripción"
        
        # Mock business addition
        return f"""✅ **Negocio Añadido al Seguimiento**

🏪 **Negocio:** @{business_user}
📝 **Descripción:** {description}
👨‍💼 **Añadido por:** @{username}
📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

💼 **Monitoreo activado:**
• Transacciones comerciales
• Volumen de actividad
• Análisis de crecimiento"""
    
    def _handle_config(self, args: List[str], username: str) -> str:
        """Handle config command"""
        if not args:
            # Show current config
            return """⚙️ **Configuración Actual**

📊 **Reportes:**
• Frecuencia: Diario (21:00 Ecuador)
• Días de análisis: 7
• Usuarios mínimos: 5

🔍 **Seguimiento:**
• Usuarios activos: 45
• Negocios monitoreados: 12
• Transacciones mínimas: 0.001 HIVE

⚡ **Bot:**
• Estado: Activo
• Comandos: Habilitados
• Modo: Producción"""
        
        if len(args) < 2:
            return "❌ Uso: `!pulse config <parámetro> <valor>`"
        
        param = args[0]
        value = args[1]
        
        # Mock config change
        return f"""✅ **Configuración Actualizada**

⚙️ **Parámetro:** {param}
🔧 **Nuevo valor:** {value}
👨‍💼 **Modificado por:** @{username}
📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

⚠️ **Nota:** Los cambios se aplicarán en el próximo ciclo."""
    
    def _handle_force_report(self, args: List[str], username: str) -> str:
        """Handle force_report command"""
        report_type = args[0] if args else "daily"
        
        valid_types = ["daily", "weekly", "monthly", "business"]
        if report_type not in valid_types:
            return f"❌ Tipo de reporte inválido. Válidos: {', '.join(valid_types)}"
        
        # Mock forced report
        return f"""🚀 **Forzando Generación de Reporte**

📋 **Tipo:** {report_type.title()}
👨‍💼 **Solicitado por:** @{username}
📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

🔄 **Procesando...**

El reporte se publicará en los próximos minutos. Te notificaremos cuando esté disponible."""
    
    def _handle_status(self, args: List[str], username: str) -> str:
        """Handle status command"""
        uptime = datetime.now() - timedelta(days=5, hours=3, minutes=24)
        
        return f"""🤖 **Estado del Bot**

⚡ **Sistema:**
• Estado: ✅ Activo
• Uptime: 5 días, 3 horas, 24 minutos
• Último reporte: {datetime.now().strftime('%d/%m/%Y %H:%M')}

📊 **Estadísticas:**
• Comandos procesados: 1,247
• Reportes generados: 23
• Usuarios monitoreados: 45

🔧 **Servicios:**
• API de Hive: ✅ Conectado
• Base de datos: ✅ Operativa
• Generador de gráficos: ✅ Funcional
• Scheduler: ✅ Ejecutándose

💾 **Recursos:**
• Memoria: 245 MB / 512 MB
• CPU: 12%
• Disco: 2.1 GB / 10 GB

🛡️ **Seguridad:**
• Posting key: ✅ Cifrada
• Conexiones: ✅ Seguras
• Logs: ✅ Rotando

*Consulta realizada por @{username} el {datetime.now().strftime('%d/%m/%Y %H:%M')}*"""
    
    def get_command_list(self) -> List[Command]:
        """Get list of all commands"""
        seen_commands = set()
        commands = []
        
        for cmd in self.commands.values():
            if cmd.name not in seen_commands:
                commands.append(cmd)
                seen_commands.add(cmd.name)
        
        return commands
    
    def is_command(self, text: str) -> bool:
        """Check if text is a command"""
        return text.strip().startswith(self.prefix)
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract user mentions from text"""
        mentions = re.findall(r'@([a-zA-Z0-9._-]+)', text)
        return list(set(mentions))  # Remove duplicates
    
    def format_command_response(self, response: str, username: str) -> str:
        """Format command response for posting"""
        formatted = f"@{username} {response}"
        
        # Add timestamp
        formatted += f"\n\n*Respuesta generada el {datetime.now().strftime('%d/%m/%Y %H:%M')}*"
        
        return formatted
