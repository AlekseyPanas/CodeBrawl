package com.sentibyte

import ujson.{Arr, Obj}

import java.io.DataInputStream
import java.io.DataOutputStream
import java.io.IOException
import java.net.Socket
import java.nio.charset.Charset
import java.util.Arrays

object Main extends App {
  // Command JSON to be sent to the server
  val velocity: Arr = ujson.Arr(
    0.0,
    0.0
  )

  val commands: Obj = ujson.Obj(
    "is_movement_command" -> false,
    "movement_command_vectors" -> velocity,
    "is_shoot_regular_bullet_command" -> false,
    "shoot_regular_bullet_angle" -> 0.0,
    "is_shoot_highvel_bullet_command" -> false,
    "shoot_highvel_bullet_angle" -> 0.0,
    "is_shoot_missile_command" -> false,
    "shoot_missile_target_id" -> 0,
    "is_use_sword_command" -> false,
    "use_sword_angle" -> 0.0,
  )
  var has_shot: Boolean = false

  // (since game_data differentiates powerups based on a numerical ID, without this you would not be able to identify)
  val MISSILE_AMMO: Int = 0
  val ENERGY: Int = 1
  val REGULAR_AMMO: Int = 2
  val HIGHVEL_AMMO: Int = 3

  println("Hello World")
  // "98.113.73.8"; // The server's hostname or IP address
  val HOST: String = "127.0.0.1"
  // The port used by the server
  val PORT: Int = 42069
  val client: Client = new Client(HOST, PORT)
  client.connect()

  def setup(): Array[Byte] = ujson.Obj(
    "NAME" -> "Your Player Name",
    "MOD_HEALTH" -> 0,
    "MOD_FORCE" -> 0,
    "MOD_SWORD" -> 0,
    "MOD_DAMAGE" -> 0,
    "MOD_SPEED" -> 0,
    "MOD_ENERGY" -> 0,
    "MOD_DODGE" -> 0
  ).toString().getBytes

  // CHANGE THE VALUES TO SET YOUR MODS AND NAME STRING!
  // DO NOT EXCEED A SUM OF 26 FOR YOUR MODS!
  // DO NOT TOUCH THE KEY NAMES!
  // CHANGE THE VALUES TO SET YOUR MODS AND NAME STRING!
  // DO NOT EXCEED A SUM OF 26 FOR YOUR MODS!
  // DO NOT TOUCH THE KEY NAMES!

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
  def update(game_data: Obj): Unit = {}

  def reset(): Unit = {
    has_shot = false
    commands("is_movement_command") = false
    commands("is_shoot_regular_bullet_command") = false
    commands("is_shoot_highvel_bullet_command") = false
    commands("is_shoot_missile_command") = false
    commands("is_use_sword_command") = false
  }

  /**
   * Call this function to move your player
   *
   * @param horizontal_vector A number between -1 and 1 representing the fraction of the speed to move horizontally
   * @param vertical_vector   A number between -1 and 1 representing the fraction of the speed to move vertically
   */
  def move(horizontal_vector: Double, vertical_vector: Double): Unit = {
    velocity(0) = horizontal_vector
    velocity(1) = vertical_vector
    commands("is_movement_command") = true
    commands("movement_command_vectors") = velocity
  }

  /**
   * Call this function to shoot a regular bullet
   *
   * @param angle A number representing the angle, in degrees, at which you want to fire your ammo
   */
  def shoot_regular(angle: Double): Unit = {
    if (has_shot) {
      println(
        "WARNING: You cannot shoot multiple projectiles at once! 'shoot_regular' command cancelled!")
    } else {
      has_shot = true
      commands("is_shoot_regular_bullet_command") = true
      commands("shoot_regular_bullet_angle") = angle
    }
  }

  /**
   * Call this function to shoot a high velocity bullet (increased speed)
   *
   * @param angle A number representing the angle, in degrees, at which you want to fire your ammo
   */
  def shoot_highvel(angle: Double): Unit = {
    if (has_shot) {
      println(
        "WARNING: You cannot shoot multiple projectiles at once! 'shoot_highvel' command cancelled!")
    } else {
      has_shot = true
      commands("is_shoot_highvel_bullet_command") = true
      commands("shoot_highvel_bullet_angle") = angle
    }
  }

  /**
   * Call this function to shoot a missile at a target player
   *
   * @param target_id The player ID of the player you would like the missile to target
   */
  def shoot_missile(target_id: Int): Unit = {
    if (has_shot) {
      println(
        "WARNING: You cannot shoot multiple projectiles at once! 'shoot_missile' command cancelled!")
    } else {
      has_shot = true
      commands("is_shoot_missile_command") = true
      commands("shoot_missile_target_id") = target_id
    }
  }

  /**
   * Call this to deploy your sword for a brief period of time in the specified direction
   *
   * @param angle A number representing the angle, in degrees, at which you want to stab your sword
   */
  def use_sword(angle: Double): Unit = {
    commands("is_use_sword_command") = true
    commands("use_sword_angle") = angle
  }

}

class Client(private val HOST: String, private val PORT: Int) {

  def connect(): Unit = {
    // initialize socket and input output streams
    val socket: Socket = new Socket(HOST, PORT)
    val input: DataInputStream = new DataInputStream(socket.getInputStream)
    val output: DataOutputStream = new DataOutputStream(socket.getOutputStream)
    // send initial mods data
    output.write(Main.setup())

    try {
      while (input.readByte() != 115) {
        output.write(1)
      }

      // initiates communications loop
      while (true) {
        // receives game data
        var game_data: Array[Byte] = Array.ofDim[Byte](131072)
        val bytes: Int = input.read(game_data)

        // breaks if data ends connection
        if (bytes >= 0) {
          // clears commands
          Main.reset()
          // calls logic function with parsed json game data
          Main.update(ujson.read(Arrays.copyOfRange(game_data, 0, bytes)).obj)
          // sends commands

          output.write(ujson.write(Main.commands).getBytes(Charset.forName("UTF-8")))
        }
      }
    } finally {
      // close the connection
      socket.close()
      input.close()
      output.close()
    }
  }

}
