using UnityEngine;
using System;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using UnityEngine.UI;
using TMPro;

public class UDPReceive2 : MonoBehaviour
{
    Thread receiveThread;
    UdpClient client;
    public int port = 5052;
    public bool startRecieving = true;
    public bool printToConsole = false;
    public string data;
    public TextMeshProUGUI random_animal;

    bool change = false;

    public void Start()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }
    void Update()
    {
        if (change)
        {
            edit_animal();
        }
    }

    private void ReceiveData()
    {
        client = new UdpClient(port);
        while (startRecieving)
        {
            try
            {
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                byte[] dataByte = client.Receive(ref anyIP);
                data = Encoding.UTF8.GetString(dataByte);
                if(data != null)change = true;
                if (printToConsole)
                {
                    Debug.Log(data);
                }
            }
            catch (Exception err)
            {
                //Debug.Log(err.ToString);
            }
        }
    }
    public void edit_animal()
    {
        random_animal.text = data;
    }

    private void OnDestroy()
    {
        client.Close();
    }
}
