using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Diagnostics;

public class startServer : MonoBehaviour
{
    [SerializeField] private bool CanStart = true;
    [SerializeField] private string ScriptFolder = "C:/Users/Asus-FX517Z/Desktop/sever2/";
    [SerializeField] private string ScriptName = "";
    [SerializeField] private int delayForStartServer;
    [SerializeField] private Dec dec;


    IEnumerator StartServer()
    {
        Process.Start(ScriptFolder + ScriptName + ".vbs");
        UnityEngine.Debug.LogWarning("Server Has Started");
        yield return new WaitForSeconds(delayForStartServer);
        if (dec != null)
        {

            dec.enabled = true;
        }
    }
    public void ServerStart()
    {
        if (CanStart)
        {
            StartCoroutine(StartServer());
        }
    }

    private void Awake()
    {

        ServerStart();
    }
}

