using System.Collections;
using System.Collections.Generic;
using UnityEngine;

using System;
using System.Threading;
using System.Net;
using System.Net.Sockets;
using System.Text;

public class UnityChanController : MonoBehaviour, UnityChanISaveable
{
    private Animator anim;

    public SkinnedMeshRenderer ref_SMR_EYE_DEF;
    public SkinnedMeshRenderer ref_SMR_EL_DEF;

    public float max_rotation_angle = 45.0f;

    public float ear_max_threshold = 0.38f;
    public float ear_min_threshold = 0.30f;

    public bool isAutoBlinkActive;
    private MonoBehaviour autoBlinkScript;

    [HideInInspector]
    public float eye_ratio_close = 85.0f;
    [HideInInspector]
    public float eye_ratio_half_close = 20.0f;
    [HideInInspector]
    public float eye_ratio_open = 0.0f;
    public SkinnedMeshRenderer ref_SMR_MTH_DEF;

    public float mar_max_threshold = 1.0f;
    public float mar_min_threshold = 0.0f;

    private Transform neck;
    private Quaternion neck_quat;

    Thread receiveThread;
    TcpClient client;
    TcpListener listener;
    int port = 8000;

    private float roll = 0, pitch = 0, yaw = 0;
    private float ear_left = 0, ear_right = 0;
    private float mar = 0;

    void Start()
    {
        anim = GetComponent<Animator>();
        neck = anim.GetBoneTransform(HumanBodyBones.Neck);
        neck_quat = Quaternion.Euler(0, 90, -90);
        autoBlinkScript = GetComponent("AutoBlink") as MonoBehaviour;
        autoBlinkScript.enabled = isAutoBlinkActive;
        SetEyes(eye_ratio_open);
        InitTCP();
    }

    private void InitTCP()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }

    private void ReceiveData()
    {
        try
        {
            listener = new TcpListener(IPAddress.Parse("127.0.0.1"), port);
            listener.Start();
            Byte[] bytes = new Byte[1024];

            while (true)
            {
                using (client = listener.AcceptTcpClient())
                {
                    using (NetworkStream stream = client.GetStream())
                    {
                        int length;
                        while ((length = stream.Read(bytes, 0, bytes.Length)) != 0)
                        {
                            var incommingData = new byte[length];
                            Array.Copy(bytes, 0, incommingData, 0, length);
                            string clientMessage = Encoding.ASCII.GetString(incommingData);
                            string[] res = clientMessage.Split(' ');
                            roll = float.Parse(res[0]);
                            pitch = float.Parse(res[1]);
                            yaw = float.Parse(res[2]);
                            ear_left = float.Parse(res[3]);
                            ear_right = float.Parse(res[4]);
                            mar = float.Parse(res[9]);
                        }
                    }
                }
            }
        }
        catch (Exception e)
        {
            print(e.ToString());
        }
    }

    void Update()
    {
        print(string.Format("Roll: {0:F}; Pitch: {1:F}; Yaw: {2:F}", roll, pitch, yaw));

        HeadRotation();

        if (!isAutoBlinkActive)
            EyeBlinking();

        MouthMoving();
    }

    void HeadRotation()
    {
        float pitch_clamp = Mathf.Clamp(pitch, -max_rotation_angle, max_rotation_angle);
        float yaw_clamp = Mathf.Clamp(yaw, -max_rotation_angle, max_rotation_angle);
        float roll_clamp = Mathf.Clamp(roll, -max_rotation_angle, max_rotation_angle);
        neck.rotation = Quaternion.Euler(pitch_clamp, yaw_clamp, roll_clamp) * neck_quat;
    }

    void EyeBlinking()
    {
        float ear_min = Mathf.Min(ear_left, ear_right);
        ear_min = Mathf.Clamp(ear_min, ear_min_threshold, ear_max_threshold);
        float x = Mathf.Abs((ear_min - ear_min_threshold) / (ear_max_threshold - ear_min_threshold) - 1);
        float y = 90 * Mathf.Pow(x, 2) - 5 * x;
        SetEyes(y);
    }

    void SetEyes(float ratio)
    {
        ref_SMR_EYE_DEF.SetBlendShapeWeight(6, ratio);
        ref_SMR_EL_DEF.SetBlendShapeWeight(6, ratio);
    }

    public void EnableAutoBlink(bool enabled)
    {
        autoBlinkScript.enabled = enabled;
        isAutoBlinkActive = enabled;
    }

    void MouthMoving()
    {
        float mar_clamped = Mathf.Clamp(mar, mar_min_threshold, mar_max_threshold);
        float ratio = (mar_clamped - mar_min_threshold) / (mar_max_threshold - mar_min_threshold);
        ratio = ratio * 100 / (mar_max_threshold - mar_min_threshold);
        SetMouth(ratio);
    }

    void SetMouth(float ratio)
    {
        ref_SMR_MTH_DEF.SetBlendShapeWeight(2, ratio);
    }

    void OnApplicationQuit()
    {
        receiveThread.Abort();
    }

    public void PopulateSaveData(UnityChanPref unityChanPref)
    {
        unityChanPref.max_rotation_angle = max_rotation_angle;
        unityChanPref.ear_max_threshold = ear_max_threshold;
        unityChanPref.ear_min_threshold = ear_min_threshold;
        unityChanPref.isAutoBlinkActive = isAutoBlinkActive;
        unityChanPref.mar_max_threshold = mar_max_threshold;
        unityChanPref.mar_min_threshold = mar_min_threshold;
    }

    public void LoadFromSaveData(UnityChanPref unityChanPref)
    {
        max_rotation_angle = unityChanPref.max_rotation_angle;
        ear_max_threshold = unityChanPref.ear_max_threshold;
        ear_min_threshold = unityChanPref.ear_min_threshold;
        isAutoBlinkActive = unityChanPref.isAutoBlinkActive;
        mar_max_threshold = unityChanPref.mar_max_threshold;
        mar_min_threshold = unityChanPref.mar_min_threshold;
    }
}
