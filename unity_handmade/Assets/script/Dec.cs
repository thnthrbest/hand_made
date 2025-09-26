using UnityEngine;
using UnityEngine.UI;
using System.Net.Sockets;
using System.IO;
using System;

public class Dec : MonoBehaviour
{
    public RawImage rawImage;   // Unity RawImage to display the processed image
    private WebCamTexture webcamTexture;
    public TcpClient client;
    public NetworkStream stream;
    public BinaryWriter writer;
    public BinaryReader reader;
    [Header("Script")]
    [SerializeField] private UDPSender uDPSender;

    public string serverAddress = "127.0.0.1";
    public int serverPort = 5055;

    Texture2D frame;
    Texture2D processedTexture;

    void Start()
    {


        try
        {
            // Start the webcam
            WebCamDevice[] devices = WebCamTexture.devices;
            try
            {
                webcamTexture = new WebCamTexture(devices[1].name);

            }
            catch (Exception e)
            {
                UnityEngine.Debug.LogError(e);
            }
            processedTexture = new Texture2D(2, 2);
            rawImage.texture = webcamTexture;
            webcamTexture.Play();

            frame = new Texture2D(webcamTexture.width, webcamTexture.height);


            // Connect to the Python server
            client = new TcpClient(serverAddress, serverPort);
            stream = client.GetStream();
            writer = new BinaryWriter(stream);
            reader = new BinaryReader(stream);

            if (PlayerPrefs.HasKey("threshold") && uDPSender!=null)
            {
                int thres = PlayerPrefs.GetInt("threshold") != 0 ? PlayerPrefs.GetInt("threshold") : 70;
                uDPSender.Sender(PlayerPrefs.GetInt("threshold").ToString());
            }
        }
        catch (Exception e)
        {
            UnityEngine.Debug.LogError(e);
        }
    }

    float FindFps(DateTime start)
    {
        TimeSpan elapsed = DateTime.Now - start;
        float seconds = (float)elapsed.TotalSeconds;

        if (seconds == 0)
            return 0f; // avoid divide by zero

        return 1f / seconds;
    }
    void Update()
    {
        DateTime startTime;
        // Proceed with the rest of the Update() method

        if (webcamTexture.isPlaying)
        {
            // frame = new Texture2D(webcamTexture.width, webcamTexture.height);
            frame.SetPixels(webcamTexture.GetPixels());
            frame.Apply();

            // Convert frame to JPG byte array
            byte[] bytes = frame.EncodeToJPG();

            if (writer != null)
            {
                writer.Write(bytes.Length);   // Write the length of the frame data
                writer.Write(bytes);          // Send the frame data
                writer.Flush();
                startTime = DateTime.Now;
                //UnityEngine.Debug.Log("Send");
            }
            else
            {
                // Debug.LogError("Writer is not initialized.");
                return;
            }
     

            // Wait for processed frame from Python
            try
            {
                if (reader != null)
                {
                    // Destroy(processedTexture);

                    int processedLength = reader.ReadInt32();
                    byte[] processedData = reader.ReadBytes(processedLength);
                    // processedTexture= new Texture2D(2, 2);

                    // Convert the received byte array back to a texture
                    // processedTexture = new Texture2D(2, 2);
                    processedTexture.LoadImage(processedData);
                    rawImage.texture = processedTexture;
                    // UnityEngine.Debug.Log("Recive");
                    // Do some work here
                    float fps = FindFps(startTime);
                    //UnityEngine.Debug.Log("FPS: " + fps);
                    // Destroy(frame);



                }
                else
                {
                    UnityEngine.Debug.LogError("Reader is not initialized.");
                }
            }
            catch (Exception ex)
            {
                UnityEngine.Debug.LogError($"Error while reading processed data: {ex.Message}");
            }

            // Optionally, handle received detection results (landmarks, etc.)

        }
    }


    void OnApplicationQuit()
    {
        UnityEngine.Debug.Log("Quit Dec");
        // Clean up and close connections
        writer.Close();
        reader.Close();
        stream.Close();
        client.Close();
    }

    void OnDestroy()
    {
        UnityEngine.Debug.Log("Out");
        writer.Close();
        reader.Close();
        stream.Close();
        client.Close();
        webcamTexture.Stop();
    }

}
