<!doctype html>

  <form action="index.php">
    <table align="center">
      <tr>
        <td>Serie name:</td>
        <td><input type="text" name="serieName"></td>
      </tr>
      <tr>
        <td>Season number:</td>
        <td><input type="text" name="seasonNumber"></td>
      </tr>
      <tr>
        <td>chapter number:</td>
        <td><input type="text" name="chapterNumber"></td>
      <tr>
        <td colspan="2" align="center"></br><input type="submit" value="addToDownloadQueue"></td>
      </tr>
    </table>
  </form>

  <?php

  if ((isset ($_GET ['serieName'])) && (isset ($_GET ['seasonNumber'])) && (isset ($_GET ['chapterNumber']))){
    if ((! empty($_GET ['serieName'])) && (! empty($_GET ['seasonNumber'])) && (! empty($_GET ['chapterNumber']))){

      echo '<br>';
      $url = "http://localhost:10927/addChapterToDownloadQueue?serieName=" . str_replace (' ', '_', $_GET['serieName']) . '&seasonNumber=' . $_GET['seasonNumber'] . '&chapterNumber=' . $_GET ['chapterNumber'];

      $ch = curl_init();
      curl_setopt ($ch, CURLOPT_URL, $url);
      curl_setopt ($ch, CURLOPT_RETURNTRANSFER, true);

      $ret = curl_exec ($ch);
      curl_close ($ch);

      echo '<table align="center"><tr><td>' . $ret . '</td></tr></table>';

    }
  }

  ?>
