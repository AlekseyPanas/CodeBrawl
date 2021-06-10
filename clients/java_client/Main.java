import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.util.Arrays;

public class Main {
    // Command JSON to be sent to the server
    public static final JSONObject commands = new JSONObject();
    public static final JSONArray velocity = new JSONArray();
    public static boolean has_shot = false;

    // links powerup IDs to their corresponding power up type
    // you can choose to use this in your code, but mainly this will help you identify which integer ID value represents which powerup
    // (since game_data differentiates powerups based on a numerical ID, without this you would not be able to identify)
    public static final int MISSILE_AMMO = 0;
    public static final int ENERGY = 1;
    public static final int REGULAR_AMMO = 2;
    public static final int HIGHVEL_AMMO = 3;

    static {
        velocity.add(0.0);
        velocity.add(0.0);

        commands.put("is_movement_command", false);
        commands.put("movement_command_vectors", velocity);

        commands.put("is_shoot_regular_bullet_command", false);
        commands.put("shoot_regular_bullet_angle", 0.0);

        commands.put("is_shoot_highvel_bullet_command", false);
        commands.put("shoot_highvel_bullet_angle", 0.0);

        commands.put("is_shoot_missile_command", false);
        commands.put("shoot_missile_target_id", 0);

        commands.put("is_use_sword_command", false);
        commands.put("use_sword_angle", 0.0);
    }

    public static void main(String[] args) throws IOException, ParseException {
        System.out.println("Hello World");

        String HOST = "98.113.73.8"; // The server's hostname or IP address
        int PORT = 42069; // The port used by the server

        Client client = new Client(HOST, PORT);
        client.connect();
    }

    public static byte[] setup() {
        // CHANGE THE VALUES TO SET YOUR MODS AND NAME STRING!
        // DO NOT EXCEED A SUM OF 26 FOR YOUR MODS!
        // DO NOT TOUCH THE KEY NAMES!

        JSONObject mods = new JSONObject();
        mods.put("NAME", "Your Player Name");
        mods.put("MOD_HEALTH", 0);
        mods.put("MOD_FORCE", 0);
        mods.put("MOD_SWORD", 0);
        mods.put("MOD_DAMAGE", 0);
        mods.put("MOD_SPEED", 0);
        mods.put("MOD_ENERGY", 0);
        mods.put("MOD_DODGE", 0);
        return mods.toString().getBytes();
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
     * - < Repeat from the top >
     *
     * @param game_data a large java JSONObject containing information about the current game state
     */
    public static void update(JSONObject game_data) {
    }

    public static void reset() {
        has_shot = false;
        commands.replace("is_movement_command", false);
        commands.replace("is_shoot_regular_bullet_command", false);
        commands.replace("is_shoot_highvel_bullet_command", false);
        commands.replace("is_shoot_missile_command", false);
        commands.replace("is_use_sword_command", false);
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
     * @param horizontal_vector A number between -1 and 1 representing the fraction of the speed to move horizontally
     * @param vertical_vector   A number between -1 and 1 representing the fraction of the speed to move vertically
     */
    public static void move(double horizontal_vector, double vertical_vector) {
        velocity.set(0, horizontal_vector);
        velocity.set(1, vertical_vector);
        commands.replace("is_movement_command", true);
        commands.replace("movement_command_vectors", velocity);
    }

    /**
     * Call this function to shoot a regular bullet
     *
     * @param angle A number representing the angle, in degrees, at which you want to fire your ammo
     */
    public static void shoot_regular(double angle) {
        if (has_shot) {
            System.out.println("WARNING: You cannot shoot multiple projectiles at once! 'shoot_regular' command cancelled!");
        } else {
            has_shot = true;
            commands.replace("is_shoot_regular_bullet_command", true);
            commands.replace("shoot_regular_bullet_angle", angle);
        }
    }

    /**
     * Call this function to shoot a high velocity bullet (increased speed)
     *
     * @param angle A number representing the angle, in degrees, at which you want to fire your ammo
     */
    public static void shoot_highvel(double angle) {
        if (has_shot) {
            System.out.println("WARNING: You cannot shoot multiple projectiles at once! 'shoot_highvel' command cancelled!");
        } else {
            has_shot = true;
            commands.replace("is_shoot_highvel_bullet_command", true);
            commands.replace("shoot_highvel_bullet_angle", angle);
        }
    }

    /**
     * Call this function to shoot a missile at a target player
     *
     * @param target_id The player ID of the player you would like the missile to target
     */
    public static void shoot_missile(int target_id) {
        if (has_shot) {
            System.out.println("WARNING: You cannot shoot multiple projectiles at once! 'shoot_missile' command cancelled!");
        } else {
            has_shot = true;
            commands.replace("is_shoot_missile_command", true);
            commands.replace("shoot_missile_target_id", target_id);
        }
    }

    /**
     * Call this to deploy your sword for a brief period of time in the specified direction
     *
     * @param angle A number representing the angle, in degrees, at which you want to stab your sword
     */
    public static void use_sword(double angle) {
        commands.replace("is_use_sword_command", true);
        commands.replace("use_sword_angle", angle);
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

class Client {
    private final String HOST;
    private final int PORT;

    public Client(String host, int port) {
        HOST = host;
        PORT = port;
    }

    public void connect() throws IOException, ParseException {
        // initialize socket and input output streams
        Socket socket = new Socket(HOST, PORT);
        DataInputStream input = new DataInputStream(socket.getInputStream());
        DataOutputStream output = new DataOutputStream(socket.getOutputStream());

        // send initial mods data
        output.write(Main.setup());

        while (true) {
            byte[] buffer = new byte[1];
            int bytes = input.read(buffer);

            if (bytes == -1 || (new String(Arrays.copyOfRange(buffer, 0, bytes))).equals("s")) {
                break;
            }

            output.write(new byte[]{1});
        }

        // initiates communications loop
        while (true) {
            // receives game data
            byte[] game_data = new byte[131072];
            int bytes = input.read(game_data);

            // breaks if data ends connection
            if (bytes == -1) break;

            // clears commands
            Main.reset();

            // calls logic function with parsed json game data
            Main.update((JSONObject) (new JSONParser()).parse(new String(Arrays.copyOfRange(game_data, 0, bytes))));

            // sends commands
            output.write(Main.commands.toString().getBytes());
        }

        // close the connection
        input.close();
        output.close();
        socket.close();
    }
}