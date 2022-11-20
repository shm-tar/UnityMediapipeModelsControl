using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class ButtonHover : MonoBehaviour
{   
    public TMP_Text TextComponent;
    public void OnMouseOver()
    {
        TextComponent.fontStyle = FontStyles.Bold;
    }

    public void OnMouseExit()
    {
        TextComponent.fontStyle ^= FontStyles.Bold;
    }
}
