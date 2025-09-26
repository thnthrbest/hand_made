using System;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.IO;


public class manange : MonoBehaviour
{
    public UDPSender uDPSender;
    public TextMeshProUGUI rdanimal_text;
    public TextMeshProUGUI same;
    public UDPReceive uDPReceive;
    public bool play = false;
    Color color;
    string[] a;

    public RawImage animal_pic;   // Drag RawImage จาก Inspector มาใส่
    public string imagePath = "D:/Images/myPic.jpg"; // ตำแหน่งไฟล์

    void Start()
    {
    }
    public void change()
    {
        imagePath = "D:/GitHub/hand_made/unity_handmade/Assets/img/" + a[0] + ".png";

        // โหลด byte[] จากไฟล์
        byte[] fileData = File.ReadAllBytes(imagePath);

        // สร้าง Texture2D ว่าง
        Texture2D tex = new Texture2D(2, 2);

        // แปลง byte[] เป็นรูป
        tex.LoadImage(fileData);

        // เอาไปใส่ใน RawImage
        animal_pic.texture = tex;
        play = false;

        if(!play){animal_pic.gameObject.SetActive(true);
        Debug.Log("ควยเปิด");}

        
    }
    public void start_shadow()
    {
        if (uDPReceive != null)
        {
            animal_pic.gameObject.SetActive(false);
            Debug.Log("ควย+ปิด");
            a = (uDPReceive.data).Split(' ');
            rdanimal_text.text = a[0];
            Debug.Log(a[0]);
            if (((float.Parse(a[1])) * 100) >= 70)
            {
                if (ColorUtility.TryParseHtmlString("#00FF00", out color)) same.color = color;
                same.text = ((float.Parse(a[1])) * 100) + " %";
                Invoke("change", 5f);
                play = false;
            }
            if (((float.Parse(a[1])) * 100) < 70) if (ColorUtility.TryParseHtmlString("#FFD300", out color))
                {
                    same.color = color;
               same.text = ((float.Parse(a[1])) * 100) + " %"; 
            } 
            
        }
    }


    void Update()
    {
        if(play)
        {
            Invoke("start_shadow", 0.5f);
        }
    }
}
//rabbit,elephent,snail,dog,deer,cow,crab,bird