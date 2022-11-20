using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HiyoriAnimationsSet : MonoBehaviour
{
    public Animator hiyoriAnim;

    IEnumerator Start()
    {
        hiyoriAnim = gameObject.GetComponent<Animator>();

        while (true)
        {
            yield return new WaitForSeconds(1);

            hiyoriAnim.SetInteger("idle_index", Random.Range(0, 9));
            hiyoriAnim.SetTrigger("idle");
        }
    }
}