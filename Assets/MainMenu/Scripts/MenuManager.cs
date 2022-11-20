using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;  

public class MenuManager : MonoBehaviour
{
    public GameObject gameScenePanelToClose;
    public GameObject gameScenePanelToOpen;
    public Animator crossFade;
    public string sceneToLoadLive2D;
    public string sceneToLoadUnityChan;
    public string sceneToLoadMainMenu;

    void Start()
    {
        gameScenePanelToOpen.SetActive(false);
    }
    
    public void OpenSceneSelectionPanel()
    {
        if (gameScenePanelToOpen != null & gameScenePanelToClose != null)
        {
            gameScenePanelToClose.SetActive(false);
            gameScenePanelToOpen.SetActive(true);
        }
    }

    public void CloseSceneSelectionPanel()
    {
        if (gameScenePanelToOpen != null & gameScenePanelToClose != null)
        {
            gameScenePanelToClose.SetActive(true);
            gameScenePanelToOpen.SetActive(false);
        }
    }

    IEnumerator CrossFadeTransition(string sceneToLoad)
    {
        crossFade.SetTrigger("Start");
        yield return new WaitForSeconds(1);
        SceneManager.LoadScene(sceneToLoad);
    }

    public void LoadLive2DScene()
    {
        StartCoroutine(CrossFadeTransition(sceneToLoadLive2D));
    }

    public void LoadUnityChanScene()
    {
        StartCoroutine(CrossFadeTransition(sceneToLoadUnityChan));
    }

    public void LoadMainMenuScene()
    {
        StartCoroutine(CrossFadeTransition(sceneToLoadMainMenu));
    }

    public void ExitGame()
    {
        // StartCoroutine(CrossFadeTransition());
        Application.Quit();
    }
}
