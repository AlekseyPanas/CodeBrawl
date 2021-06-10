using System;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;

namespace CodeBrawl
{
    class Program
    {
        // links powerup IDs to their corresponding power up type
        // you can choose to use this in your code, but mainly this will help you identify which integer ID value represents which powerup
        // (since game_data differentiates powerups based on a numerical ID, without this you would not be able to identify)
        public static readonly int MISSILE_AMMO = 0;
        public static readonly int ENERGY = 1;
        public static readonly int REGULAR_AMMO = 2;
        public static readonly int HIGHVEL_AMMO = 3;

        public static bool has_shot = false;

        // Command JSON to be sent to the server
        public static Commands commands = new()
        {
            is_movement_command = false,
            movement_command_vectors = new double[] { 0, 0 },
            is_shoot_regular_bullet_command = false,
            shoot_regular_bullet_angle = 0,
            is_shoot_highvel_bullet_command = false,
            shoot_highvel_bullet_angle = 0,
            is_shoot_missile_command = false,
            shoot_missile_target_id = 0,
            is_use_sword_command = false,
            use_sword_angle = 0,
        };

        static void Main(string[] args)
        {
            Console.WriteLine("Hello World");

            String HOST = "98.113.73.8"; // The server's hostname or IP address
            Int32 PORT = 42069; // The port used by the server

            Client client = new(HOST, PORT);
            client.connect();
        }

        public static byte[] setup()
        {
            // CHANGE THE VALUES TO SET YOUR MODS AND NAME STRING!
            // DO NOT EXCEED A SUM OF 26 FOR YOUR MODS!
            // DO NOT TOUCH THE KEY NAMES!

            return Encoding.UTF8.GetBytes(JsonSerializer.Serialize(new Player
            {
                NAME = "whatever you want",
                MOD_HEALTH = 0,
                MOD_FORCE = 0,
                MOD_SWORD = 0,
                MOD_DAMAGE = 0,
                MOD_SPEED = 26,
                MOD_ENERGY = 0,
                MOD_DODGE = 0
            }));
        }

        /**
         * This is your update function where you will write all the logic for your player!
         * <p>
         * Feel free to import libraries, create classes, functions, or variables to suit your needs!
         * <p>
         * Order of events within the game
         * - Server executes next frame
         * - Server gathers game state information
         * - Server sends game state info to clients
         * - Client (this file) calls the update function providing you with game_data
         * - Client sends commands that you executed back to the server
         * - [ Repeat from the top ]
         *
         * @param game_data a large c# JSONObject containing information about the current game states
         */
        public static void update(GameData game_data)
        {

        }

        public static void reset()
        {
            has_shot = false;
            commands.is_movement_command = false;
            commands.is_shoot_regular_bullet_command = false;
            commands.is_shoot_highvel_bullet_command = false;
            commands.is_shoot_missile_command = false;
            commands.is_use_sword_command = false;
        }

        /*
         ******************************************************************************************************
         * Commands
         ******************************************************************************************************
         * ░█▀▀█ ░█▀▀▀█ ░█▀▄▀█ ░█▀▄▀█ ─█▀▀█ ░█▄─░█ ░█▀▀▄ ░█▀▀▀█
         * ░█─── ░█──░█ ░█░█░█ ░█░█░█ ░█▄▄█ ░█░█░█ ░█─░█ ─▀▀▀▄▄
         * ░█▄▄█ ░█▄▄▄█ ░█──░█ ░█──░█ ░█─░█ ░█──▀█ ░█▄▄▀ ░█▄▄▄█
         ******************************************************************************************************
         * Call the commands below from inside the update function above
         * DO NOT actually change any of the code below this divider
         ******************************************************************************************************
         */

        /**
         * Call this function to move your player
         *
         * @param horizontal_vector A number between 0 and 1 representing the fraction of the speed to move horizontally
         * @param vertical_vector   A number between 0 and 1 representing the fraction of the speed to move vertically
         */
        public static void move(double horizontal_vector, double vertical_vector)
        {
            commands.is_movement_command = true;
            commands.movement_command_vectors[0] = horizontal_vector;
            commands.movement_command_vectors[1] = vertical_vector;
        }

        /**
         * Call this function to shoot a regular bullet
         *
         * @param angle A number representing the angle, in degrees, at which you want to fire your ammo
         */
        public static void shoot_regular(double angle)
        {
            if (has_shot)
            {
                Console.WriteLine("WARNING: You cannot shoot multiple projectiles at once! 'shoot_regular' command cancelled!");
            }
            else
            {
                has_shot = true;
                commands.is_shoot_regular_bullet_command = true;
                commands.shoot_regular_bullet_angle = angle;
            }
        }

        /**
         * Call this function to shoot a high velocity bullet (increased speed)
         *
         * @param angle A number representing the angle, in degrees, at which you want to fire your ammo
         */
        public static void shoot_highvel(double angle)
        {
            if (has_shot)
            {
                Console.WriteLine("WARNING: You cannot shoot multiple projectiles at once! 'shoot_highvel' command cancelled!");
            }
            else
            {
                has_shot = true;
                commands.is_shoot_highvel_bullet_command = true;
                commands.shoot_highvel_bullet_angle = angle;
            }
        }

        /**
         * Call this function to shoot a missile at a target player
         *
         * @param target_id The player ID of the player you would like the missile to target
         */
        public static void shoot_missile(int target_id)
        {
            if (has_shot)
            {
                Console.WriteLine("WARNING: You cannot shoot multiple projectiles at once! 'shoot_missile' command cancelled!");
            }
            else
            {
                has_shot = true;
                commands.is_shoot_missile_command = true;
                commands.shoot_missile_target_id = target_id;
            }
        }

        /**
         * Call this to deploy your sword for a brief period of time in the specified direction
         *
         * @param angle A number representing the angle, in degrees, at which you want to stab your sword
         */
        public static void use_sword(double angle)
        {
            commands.is_use_sword_command = true;
            commands.use_sword_angle = angle;
        }

        public class Player
        {
            public String NAME { get; set; }
            public int MOD_HEALTH { get; set; }
            public int MOD_FORCE { get; set; }
            public int MOD_SWORD { get; set; }
            public int MOD_DAMAGE { get; set; }
            public int MOD_SPEED { get; set; }
            public int MOD_ENERGY { get; set; }
            public int MOD_DODGE { get; set; }
        }

        public class Commands
        {
            public bool is_movement_command { get; set; }
            public double[] movement_command_vectors { get; set; }
            public bool is_shoot_regular_bullet_command { get; set; }
            public double shoot_regular_bullet_angle { get; set; }
            public bool is_shoot_highvel_bullet_command { get; set; }
            public double shoot_highvel_bullet_angle { get; set; }
            public bool is_shoot_missile_command { get; set; }
            public int shoot_missile_target_id { get; set; }
            public bool is_use_sword_command { get; set; }
            public double use_sword_angle { get; set; }
        }
    }

    class GameData
    {
        public int[] screen_size { get; set; }
        public Player[] players { get; set; }
        public CommandSuccess command_success { get; set; }
        public RegularBullet[] regular_bullets { get; set; }
        public HighvelBullet[] highvel_bullets { get; set; }
        public Missile[] missiles { get; set; }
        public Sword[] swords { get; set; }
        public Powerup[] powerups { get; set; }

        public class Player
        {
            public int id { get; set; }
            public bool is_you { get; set; }
            public String display_name { get; set; }
            public double[] location { get; set; }
            public double speed { get; set; }
            public double radius { get; set; }
            public double health { get; set; }
            public double energy { get; set; }
            public double shoot_cooldown { get; set; }
            public int regular_bullet_ammo { get; set; }
            public int highvel_bullet_ammo { get; set; }
            public int missile_bullet_ammo { get; set; }
        }

        public class CommandSuccess
        {
            public bool[] movement { get; set; }
            public bool shoot_ammo { get; set; }
            public bool use_sword { get; set; }
        }

        public class RegularBullet
        {
            public int id { get; set; }
            public int shooter_id { get; set; }
            public double speed { get; set; }
            public double radius { get; set; }
            public double[] location { get; set; }
            public double[] vector { get; set; }
        }

        public class HighvelBullet
        {
            public int id { get; set; }
            public int shooter_id { get; set; }
            public double speed { get; set; }
            public double radius { get; set; }
            public double[] location { get; set; }
            public double[] vector { get; set; }
        }

        public class Missile
        {
            public int id { get; set; }
            public int shooter_id { get; set; }
            public int target_id { get; set; }
            public double speed { get; set; }
            public double radius { get; set; }
            public double[] location { get; set; }
            public double angle { get; set; }
            public double[] vector { get; set; }
        }

        public class Sword
        {
            public int id { get; set; }
            public int wielder_id { get; set; }
            public double[] location { get; set; }
            public double radius { get; set; }
            public bool is_blocked { get; set; }
            public bool is_cooldown { get; set; }
            public int[] hit_objects { get; set; }
        }

        public class Powerup
        {
            public int id { get; set; }
            public double[] location { get; set; }
            public double radius { get; set; }
            public int type_id { get; set; }
        }
    }

    /*
     ******************************************************************************************************
     * ████████╗░█████╗░██████╗░ ░█████╗░░█████╗░██████╗░███████╗
     * ╚══██╔══╝██╔══██╗██╔══██╗ ██╔══██╗██╔══██╗██╔══██╗██╔════╝
     * ░░░██║░░░██║░░╚═╝██████╔╝ ██║░░╚═╝██║░░██║██║░░██║█████╗░░
     * ░░░██║░░░██║░░██╗██╔═══╝░ ██║░░██╗██║░░██║██║░░██║██╔══╝░░
     * ░░░██║░░░╚█████╔╝██║░░░░░ ╚█████╔╝╚█████╔╝██████╔╝███████╗
     * ░░░╚═╝░░░░╚════╝░╚═╝░░░░░ ░╚════╝░░╚════╝░╚═════╝░╚══════╝
     ******************************************************************************************************
     ******************************************************************************************************
     * Definitely do not tamper with code below this divider
     * Tampering with it could prevent you from properly connecting and interacting with the server
     ******************************************************************************************************
     */

    class Client
    {
        private readonly String HOST;
        private readonly Int32 PORT;

        public Client(String host, Int32 port)
        {
            HOST = host;
            PORT = port;
        }

        public void connect()
        {
            // initialize socket and input output streams
            TcpClient client = new(HOST, PORT);
            NetworkStream stream = client.GetStream();

            // send initial mods data
            stream.Write(Program.setup());

            while (true)
            {
                byte[] buffer = new byte[1];
                int bytes = stream.Read(buffer);

                if (bytes == -1 || Encoding.UTF8.GetString(buffer, 0, bytes).Equals("s"))
                {
                    break;
                }

                stream.Write(new byte[] { 1 });
            }

            // initiates communications loop
            while (true)
            {
                // receives game data
                byte[] game_data = new byte[131072];
                int bytes = stream.Read(game_data);

                // breaks if data ends connection
                if (bytes == -1) break;

                // clears commands
                Program.reset();

                // calls logic function with parsed json game data
                Program.update(JsonSerializer.Deserialize<GameData>(Encoding.UTF8.GetString(game_data, 0, bytes)));

                // sends commands
                stream.Write(Encoding.UTF8.GetBytes(JsonSerializer.Serialize(Program.commands)));
            }

            // close the connection
            stream.Close();
            client.Close();
        }
    }
}